/* Optional on-device French Pocket TTS reader for Bulle Bleue.
 * Adapted from jean-is/jean (MIT): https://github.com/jean-is/jean
 * Model and voice attribution: see NOTICE.md.
 */
import { InferenceSession, Tensor, env } from 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.1/dist/ort.webgpu.bundle.min.mjs';
import { expand, tokenizer, chunks, continuationPrompt, teacherForcedSequence, packLatents, advanceDecoderSteps } from './pocket.mjs';
import { spelled } from './words.mjs';

const RUNTIME='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.1/dist/';
env.wasm.wasmPaths={
  wasm:new URL('ort-wasm-simd-threaded.asyncify.wasm',RUNTIME).href,
  mjs:new URL('ort-wasm-simd-threaded.asyncify.mjs',RUNTIME).href
};
env.wasm.numThreads=1;

const HOST='https://huggingface.co/';
const MODEL_PATH='jean-is/pocket-tts-q8-ONNX/resolve/b94b57dd6e20af2a8d79779fef5a8e60dbe9fc51/';
const MANIFEST_HASH='7d08c86ba5cc8427d95659ead36704a977695b4a98a41270f677e675a2710e2e';
const CACHE_NAME='bb-pocket-tts-v1';
const ARRAYS={float32:Float32Array,int64:BigInt64Array,bool:Uint8Array};
let shared=null;
let current=null;
const aborted=new Set();
let busy=Promise.resolve();

async function matchesHash(data,expected){
  const digest=new Uint8Array(await crypto.subtle.digest('SHA-256',data));
  return Array.from(digest,(byte)=>byte.toString(16).padStart(2,'0')).join('')===expected;
}
async function download(url,hash,progress){
  const cache=await globalThis.caches?.open(CACHE_NAME).catch(()=>null);
  const hit=await cache?.match(url);
  if(hit){
    const saved=await hit.arrayBuffer();
    if(await matchesHash(saved,hash))return saved;
    await cache.delete(url);
  }
  const response=await fetch(url);
  if(!response.ok||!response.body)throw new Error(url+': HTTP '+response.status);
  const reader=response.body.getReader(),parts=[];
  let bytes=0,told=performance.now();
  while(true){
    const part=await reader.read();
    if(part.done)break;
    parts.push(part.value);bytes+=part.value.length;
    if(performance.now()-told>=100){progress(bytes);told=performance.now()}
  }
  const packed=new Uint8Array(bytes);
  let offset=0;
  for(const part of parts){packed.set(part,offset);offset+=part.length}
  progress(bytes);
  if(!(await matchesHash(packed.buffer,hash)))throw new Error(url+': SHA-256 mismatch');
  try{await cache?.put(url,new Response(packed.buffer.slice(0)))}catch(error){/* storage may be unavailable or full */}
  return packed.buffer;
}
const session=(bin,graph,name)=>InferenceSession.create(
  new Uint8Array(bin,graph.graph[0],graph.graph[1]),
  {executionProviders:['wasm'],externalData:[{path:name+'.f32',data:expand(bin,graph)}]}
);

async function language(lang,id){
  const loaded=await current?.catch(()=>null);
  if(loaded?.lang===lang)return loaded;
  await Promise.all(Object.values(loaded?.sessions??{}).map((one)=>one.release()));
  current=(async()=>{
    const base=new URL(MODEL_PATH+'pocket-tts.json',HOST);
    if(!shared){
      const raw=await download(base.href,MANIFEST_HASH,()=>{});
      shared={manifest:JSON.parse(new TextDecoder().decode(raw)),decoder:null};
    }
    const manifest=shared.manifest,entry=manifest.languages[lang];
    if(!entry)throw new Error('Aucune voix naturelle disponible pour la langue : '+lang);
    const total=manifest.files[entry.file][1]+(shared.decoder?0:manifest.files['decoder.bin'][1]);
    const bytes=[0,0];
    const report=(index,value)=>{
      bytes[index]=value;
      self.postMessage({id,type:'progress',loaded:bytes[0]+bytes[1],total});
    };
    const [decoder,bin]=await Promise.all([
      shared.decoder?null:download(new URL('decoder.bin',base).href,manifest.files['decoder.bin'][0],(n)=>report(0,n)),
      download(new URL(entry.file,base).href,manifest.files[entry.file][0],(n)=>report(1,n))
    ]);
    shared.decoder??=await session(decoder,manifest.decoder,'mimi_decoder');
    const sessions={};
    for(const name of ['text_conditioner','flow_lm_main','flow_lm_flow'])sessions[name]=await session(bin,entry.graphs[name],name);
    const tokens=tokenizer(JSON.parse(new TextDecoder().decode(new Uint8Array(bin,entry.tokenizer[0],entry.tokenizer[1]))));
    const [at,length]=entry.voice,voice={};
    for(const part of manifest.flow){
      const layer=Number(/layers\.(\d+)\./.exec(part.module)?.[1]);
      if(part.key==='step')voice[part.input_name]=BigInt64Array.of(BigInt(length));
      if(part.key!=='cache')continue;
      const cache=new Float32Array(part.shape.reduce((a,b)=>a*b)).fill(NaN);
      const each=length*16*64;
      for(let kv=0;kv<2;kv++)cache.set(new Float32Array(bin,at+(layer*2+kv)*each*4,each),kv*part.shape[2]*16*64);
      voice[part.input_name]=cache;
    }
    return{lang,sessions,tokens,voice,rules:entry.rules};
  })();
  current.catch(()=>{current=null});
  return current;
}
const state=(manifest,from={})=>Object.fromEntries(manifest.map((part)=>{
  const size=part.shape.reduce((a,b)=>a*b,1),Type=ARRAYS[part.dtype];
  const data=from[part.input_name]??(part.dtype==='int64'?new BigInt64Array(size):new Type(size).fill(part.fill==='nan'?NaN:part.fill==='ones'?1:0));
  return[part.input_name,new Tensor(part.dtype,data,part.shape)];
}));
async function speak({text,lang},id){
  const voice=await language(lang,id);
  /* Match Pocket TTS' continuation mode. Each bounded text chunk carries its
     predecessor's latent frames into the next chunk, so the voice, intonation
     and Mimi decoder do not restart at every sentence boundary. */
  let previousText='',previousLatents=[];
  for(const part of chunks(spelled(text,voice.lang),voice.tokens,voice.rules,25)){
    if(aborted.has(id))return;
    const partText=voice.tokens.decode(part.ids);
    const prompt=previousLatents.length
      ? continuationPrompt(previousText,partText,voice.tokens,voice.rules)
      : {text:partText,ids:part.ids};
    const generatedLatents=[];
    await say(voice,prompt.ids,part.after,id,previousLatents,generatedLatents);
    previousText=partText;
    previousLatents=generatedLatents;
  }
}
async function say({sessions,voice,rules},ids,after,id,forcedLatents=[],generatedLatents=[]){
  const {manifest,decoder}=shared;
  let flow=state(manifest.flow,voice);
  const step=async(sequence,text)=>{
    const out=await sessions.flow_lm_main.run({sequence:new Tensor('float32',sequence,[1,sequence.length/32,32]),text_embeddings:text,...flow});
    flow=Object.fromEntries(manifest.flow.map((part)=>[part.input_name,out[part.output_name]]));
    return out;
  };
  const {embeddings}=await sessions.text_conditioner.run({token_ids:new Tensor('int64',BigInt64Array.from(ids,BigInt),[1,ids.length])});
  const forced=teacherForcedSequence(forcedLatents);
  await step(forced.sequence,embeddings);
  const none=new Tensor('float32',new Float32Array(0),[1,0,1024]);
  let mimi=state(manifest.mimi),decoded=0,end=-1,previous=forced.firstInput||new Float32Array(32).fill(NaN);
  const pending=[];
  const continuing=forcedLatents.length>0;

  /* A fresh Mimi state otherwise clicks at each text chunk. Warm it with the
     previous chunk's last 12 latent frames and discard that warm-up audio, just
     as the upstream Pocket TTS implementation does. */
  if(continuing){
    const warmup=forcedLatents.slice(-12);
    const out=await decoder.run({latent:new Tensor('float32',packLatents(warmup),[1,warmup.length,32]),...mimi});
    mimi=Object.fromEntries(manifest.mimi.map((part)=>[part.input_name,out[part.output_name]]));
    advanceDecoderSteps(manifest.mimi,mimi,16*warmup.length);
  }
  const decode=async()=>{
    const frameCount=pending.length;
    const out=await decoder.run({latent:new Tensor('float32',packLatents(pending),[1,frameCount,32]),...mimi});
    mimi=Object.fromEntries(manifest.mimi.map((part)=>[part.input_name,out[part.output_name]]));
    advanceDecoderSteps(manifest.mimi,mimi,16*frameCount);
    const audio=out.audio_frame.data.slice();
    if(!decoded&&!continuing)for(let i=0;i<Math.min(120,audio.length);i++)audio[i]*=i/120;
    decoded+=frameCount;pending.length=0;
    self.postMessage({id,type:'chunk',audio,rate:manifest.rate},[audio.buffer]);
  };
  const limit=Math.ceil((ids.length/3+2)*12.5);
  for(let frame=0;frame<limit&&!aborted.has(id);frame++){
    const out=await step(previous,none);
    if(out.eos_logit.data[0]>-4&&end<0&&frame>=6)end=frame;
    if(end>=0&&frame>=end+after)break;
    const noise=Float32Array.from({length:32},()=>normal()*Math.sqrt(rules.temperature));
    const {flow_dir}=await sessions.flow_lm_flow.run({
      c:out.conditioning,s:new Tensor('float32',[0],[1,1]),t:new Tensor('float32',[1],[1,1]),x:new Tensor('float32',noise,[1,32])
    });
    for(let i=0;i<32;i++)noise[i]+=flow_dir.data[i];
    const generated=noise.slice();
    generatedLatents.push(generated);
    pending.push((previous=noise));
    if(pending.length>=(decoded===0?2:decoded<24?4:12))await decode();
    await breathe();
  }
  if(pending.length)await decode();
}
const breathe=()=>new Promise((resolve)=>{
  const channel=new MessageChannel();channel.port1.onmessage=resolve;channel.port2.postMessage(null);
});
const normal=()=>Math.sqrt(-2*Math.log(1-Math.random()))*Math.cos(2*Math.PI*Math.random());

self.onmessage=({data})=>{
  const {id,type}=data;
  if(type==='abort'){aborted.add(data.of);return}
  busy=busy.then(()=>type==='load'?language(data.lang||'fr',id):speak(data,id))
    .then(
      ()=>self.postMessage({id,type:type==='load'?'ready':'done'}),
      (error)=>self.postMessage({id,type:'error',message:error instanceof Error?error.message:String(error)})
    )
    .then(()=>{aborted.delete(id)});
};
