/* World positions in metres. Teleport uses the tracked head offset. */
const viewpoints = [{x:0,z:1.05,yaw:0},{x:-1.5,z:0,yaw:-70},{x:.85,z:-.65,yaw:180}];
function goToView(index){
 const target=viewpoints[index],rig=document.querySelector('#rig'),head=document.querySelector('#head');
 if(!target||!rig||!head)return;
 const world=new THREE.Vector3();head.object3D.getWorldPosition(world);
 rig.object3D.position.x+=target.x-world.x;rig.object3D.position.z+=target.z-world.z;
 if(!rig.sceneEl.is('vr-mode')){rig.object3D.rotation.y=THREE.MathUtils.degToRad(target.yaw);head.components['look-controls'].yawObject.rotation.y=0;head.components['look-controls'].pitchObject.rotation.x=0;}
}
AFRAME.registerComponent('teleport-to',{schema:{index:{type:'int'}},init(){
 this.onClick=()=>goToView(this.data.index);this.el.addEventListener('click',this.onClick);
},remove(){this.el.removeEventListener('click',this.onClick);}});
/* Right thumbstick, 30 degrees per push. Values: x>0 right, x<0 left. */
AFRAME.registerComponent('snap-turn',{init(){
 this.ready=true;
 this.onThumbstick=event=>{
  const x=event.detail.x;if(Math.abs(x)<.25)this.ready=true;
  if(!this.ready||Math.abs(x)<.75)return;this.ready=false;
  const rig=document.querySelector('#rig').object3D,head=document.querySelector('#head').object3D;
  const before=new THREE.Vector3(),after=new THREE.Vector3();head.getWorldPosition(before);
  rig.rotation.y-=Math.sign(x)*Math.PI/6;rig.updateMatrixWorld(true);head.getWorldPosition(after);
  rig.position.x+=before.x-after.x;rig.position.z+=before.z-after.z;
 };
 this.el.addEventListener('thumbstickmoved',this.onThumbstick);
},remove(){this.el.removeEventListener('thumbstickmoved',this.onThumbstick);}});
/* Left thumbstick: smooth movement in the direction the head looks, with collision
   against furniture and walls. A-Frame reports y>0 as stick-down, so forward is -y.
   Keyboard (W/A/S/D, arrows) drives the same movement for the desktop preview. */
AFRAME.registerComponent('player-body',{
 schema:{speed:{default:1.4},radius:{default:.26},bodyHeight:{default:1.7},footClearance:{default:.15},minObstacleSize:{default:.06},deadZone:{default:.15},invertForward:{default:false}},
 init(){
  this.obstacles=[];this.stick={x:0,y:0};this.keys={};
  this.forward=new THREE.Vector3();this.right=new THREE.Vector3();this.headWorld=new THREE.Vector3();
  this.rig=document.querySelector('#rig');this.head=document.querySelector('#head');
  this.onThumbstick=event=>{this.stick.x=event.detail.x||0;this.stick.y=event.detail.y||0;};
  this.onKeyDown=event=>{this.keys[event.code]=true;};
  this.onKeyUp=event=>{this.keys[event.code]=false;};
  this.onModelLoaded=()=>this.buildObstacles();
  this.el.addEventListener('thumbstickmoved',this.onThumbstick);
  window.addEventListener('keydown',this.onKeyDown);window.addEventListener('keyup',this.onKeyUp);
  const model=document.querySelector('#model');
  if(model){model.addEventListener('model-loaded',this.onModelLoaded);if(model.getObject3D('mesh'))this.buildObstacles();}
 },
 buildObstacles(){
  const model=document.querySelector('#model'),root=model&&model.getObject3D('mesh');
  if(!root)return;
  root.updateMatrixWorld(true);
  const box=new THREE.Box3(),list=[];
  root.traverse(node=>{
   if(!node.isMesh||!node.geometry)return;
   box.setFromObject(node,true);
   if(!isFinite(box.min.x)||!isFinite(box.max.x))return;
   if(box.max.y<=this.data.footClearance||box.min.y>=this.data.bodyHeight)return;   // podłoga, dywan, listwy, sufit
   if(box.max.x-box.min.x<this.data.minObstacleSize&&box.max.z-box.min.z<this.data.minObstacleSize)return;   // nogi, drobiazgi
   list.push({minX:box.min.x,maxX:box.max.x,minZ:box.min.z,maxZ:box.max.z});
  });
  this.obstacles=list;
  if(this.el.sceneEl)this.el.sceneEl.emit('body-ready',{obstacles:list.length});
 },
 collides(x,z){
  const r=this.data.radius;
  for(let i=0;i<this.obstacles.length;i++){
   const o=this.obstacles[i];
   const cx=x<o.minX?o.minX:(x>o.maxX?o.maxX:x),cz=z<o.minZ?o.minZ:(z>o.maxZ?o.maxZ:z);
   const dx=x-cx,dz=z-cz;
   if(dx*dx+dz*dz<r*r)return true;
  }
  return false;
 },
 input(){
  let sideways=this.stick.x,forward=this.data.invertForward?this.stick.y:-this.stick.y;
  if(Math.abs(sideways)<this.data.deadZone)sideways=0;
  if(Math.abs(forward)<this.data.deadZone)forward=0;
  if(this.keys.KeyD||this.keys.ArrowRight)sideways+=1;
  if(this.keys.KeyA||this.keys.ArrowLeft)sideways-=1;
  if(this.keys.KeyW||this.keys.ArrowUp)forward+=1;
  if(this.keys.KeyS||this.keys.ArrowDown)forward-=1;
  return {sideways,forward};
 },
 tick(time,delta){
  if(!this.obstacles.length||!this.rig||!this.head)return;
  const input=this.input();
  if(!input.sideways&&!input.forward)return;
  const camera=this.head.getObject3D('camera')||this.head.object3D;
  camera.getWorldDirection(this.forward);this.forward.y=0;   // Camera zwraca -Z, grupa Object3D zwraca +Z
  if(this.forward.lengthSq()<1e-6)return;                 // patrzymy prosto w górę lub w dół
  this.forward.normalize();
  this.right.set(-this.forward.z,0,this.forward.x);
  const magnitude=Math.min(1,Math.hypot(input.sideways,input.forward));
  const step=this.data.speed*Math.min(delta/1000,.05)*magnitude;
  const dx=(this.forward.x*input.forward+this.right.x*input.sideways)/magnitude*step;
  const dz=(this.forward.z*input.forward+this.right.z*input.sideways)/magnitude*step;
  camera.getWorldPosition(this.headWorld);
  const stuck=this.collides(this.headWorld.x,this.headWorld.z);   // już stoimy w meblu: pozwalamy się wydostać
  const steps=Math.max(1,Math.ceil(Math.max(Math.abs(dx),Math.abs(dz))/.05));
  let movedX=0,movedZ=0;
  for(let i=0;i<steps;i++){
   const subX=dx/steps,subZ=dz/steps;
   if(stuck||!this.collides(this.headWorld.x+movedX+subX,this.headWorld.z+movedZ))movedX+=subX;
   if(stuck||!this.collides(this.headWorld.x+movedX,this.headWorld.z+movedZ+subZ))movedZ+=subZ;
  }
  this.rig.object3D.position.x+=movedX;this.rig.object3D.position.z+=movedZ;
 },
 remove(){
  this.el.removeEventListener('thumbstickmoved',this.onThumbstick);
  window.removeEventListener('keydown',this.onKeyDown);window.removeEventListener('keyup',this.onKeyUp);
  const model=document.querySelector('#model');
  if(model)model.removeEventListener('model-loaded',this.onModelLoaded);
 }
});
window.addEventListener('DOMContentLoaded',()=>{
 const scene=document.querySelector('a-scene'),model=document.querySelector('#model'),status=document.querySelector('#status'),button=document.querySelector('#enter');
 model.addEventListener('model-loaded',async()=>{status.textContent='Pokój gotowy. Rozejrzyj się.';try{if(navigator.xr&&await navigator.xr.isSessionSupported('immersive-vr')){button.disabled=false;}else{button.textContent='Otwórz tę stronę w Quest';}}catch(e){status.textContent='Podgląd 3D gotowy. VR wymaga przeglądarki Quest i HTTPS.';}});
 model.addEventListener('model-error',()=>{status.textContent='Nie udało się wczytać pokoju. Odśwież stronę.';});
 button.addEventListener('click',async()=>{try{await scene.enterVR();}catch(e){status.textContent='Nie udało się uruchomić VR. Sprawdź uprawnienia przeglądarki.';}});
 scene.addEventListener('enter-vr',()=>document.body.classList.add('in-vr'));
 scene.addEventListener('exit-vr',()=>document.body.classList.remove('in-vr'));
 document.querySelectorAll('[data-view]').forEach(el=>el.addEventListener('click',()=>goToView(Number(el.dataset.view))));
 if(document.modelContext?.registerTool){
  const lifecycle=new AbortController();
  try{Promise.resolve(document.modelContext.registerTool({name:'move_to_room_view',description:'Przenieś widok do wejścia (0), okna (1) lub kanapy (2).',inputSchema:{type:'object',properties:{index:{type:'integer',enum:[0,1,2]}},required:['index'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},execute(input){if(!Number.isInteger(input.index)||input.index<0||input.index>2)throw new Error('Nieznany punkt widokowy');goToView(input.index);return {index:input.index};}},{signal:lifecycle.signal})).catch(()=>{});}catch(e){}
  window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
 }
});
