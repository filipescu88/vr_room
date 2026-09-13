/* World positions in metres. Viewpoints serve the desktop panel and the hosted view tool. */
const viewpoints = [{x:0,z:1.05,yaw:0},{x:-1.5,z:0,yaw:-70},{x:.85,z:-.65,yaw:180},{x:-1.75,z:3.4,yaw:180}];
function goToView(index){
 const target=viewpoints[index],rig=document.querySelector('#rig'),head=document.querySelector('#head');
 if(!target||!rig||!head)return;
 const world=new THREE.Vector3();head.object3D.getWorldPosition(world);
 rig.object3D.position.x+=target.x-world.x;rig.object3D.position.z+=target.z-world.z;
 if(!rig.sceneEl.is('vr-mode')){rig.object3D.rotation.y=THREE.MathUtils.degToRad(target.yaw);head.components['look-controls'].yawObject.rotation.y=0;head.components['look-controls'].pitchObject.rotation.x=0;}
}
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
/* The solid front wall and the decorative door from pokoj.glb are replaced by
   dist/models/za-drzwiami.glb (wall with a 0.82 x 2.05 m opening) and
   dist/models/drzwi.glb. Hiding meshes at runtime is a workaround for not having the
   doorway cut in Pokoj_VR.blend; do it in Blender when the project moves back there. */
AFRAME.registerComponent('legacy-front-wall',{
 schema:{names:{default:'Ściana przednia,Drzwi dekoracyjne,Klamka'}},
 init(){
  this.hidden=[];
  this.onLoaded=()=>this.hide();
  this.el.addEventListener('model-loaded',this.onLoaded);
  if(this.el.getObject3D('mesh'))this.hide();
 },
 hide(){
  const root=this.el.getObject3D('mesh');
  if(!root)return;
  const lista=[];
  this.data.names.split(',').map(nazwa=>nazwa.trim()).filter(Boolean).forEach(nazwa=>{
   lista.push(nazwa,nazwa.replace(/\s+/g,'_'));   // GLTFLoader zamienia spacje w nazwach na podkreślenia
  });
  root.traverse(node=>{
   if(node.name&&lista.includes(node.name)&&node.visible!==false){node.visible=false;this.hidden.push(node.name);}
  });
  this.el.emit('legacy-hidden',{names:this.hidden});
 },
 remove(){this.el.removeEventListener('model-loaded',this.onLoaded);}
});
/* Door: trigger on the door opens and closes it. The hinge is the origin of the entity,
   so the leaf swings around position="-2.16 0 2.08" set in index.html. */
AFRAME.registerComponent('swing-door',{
 schema:{openAngle:{default:-90},duration:{default:1.2},blockingAngle:{default:60}},
 init(){
  this.current=0;this.target=0;
  this.onClick=()=>{this.target=this.target===0?this.data.openAngle:0;this.el.emit('door-target',{angle:this.target});};
  this.el.addEventListener('click',this.onClick);
 },
 tick(time,delta){
  if(this.current===this.target)return;
  const dt=Math.min(delta/1000,.05);
  const step=Math.abs(this.data.openAngle)/this.data.duration*dt;
  const left=this.target-this.current;
  this.current=Math.abs(left)<=step?this.target:this.current+(left>0?step:-step);
  this.el.object3D.rotation.y=THREE.MathUtils.degToRad(this.current);
 },
 open(){return Math.abs(this.current)>this.data.blockingAngle;},
 angle(){return this.current;},
 remove(){this.el.removeEventListener('click',this.onClick);}
});
/* Grab: grip picks an object of class .grabbable up, releasing puts it down on the
   surface under it (table top, sofa seat, floor). The object stays in the scene and
   follows the hand — moving an entity with gltf-model to another parent makes A-Frame
   drop its model. No physics: it is set down upright. */
AFRAME.registerComponent('grab',{
 schema:{holdOffset:{type:'vec3',default:{x:0,y:-0.15,z:-0.2}}},
 init(){
  this.held=null;
  this.hand=new THREE.Vector3();this.quat=new THREE.Quaternion();this.offset=new THREE.Vector3();
  this.onGripDown=()=>this.pick();
  this.onGripUp=()=>this.drop();
  this.el.addEventListener('gripdown',this.onGripDown);
  this.el.addEventListener('gripup',this.onGripUp);
 },
 target(){
  const raycaster=this.el.components.raycaster;
  const hits=raycaster&&raycaster.intersectedEls?raycaster.intersectedEls:[];
  for(let i=0;i<hits.length;i++){if(hits[i].classList.contains('grabbable'))return hits[i];}
  return null;
 },
 follow(){                                      // prowadź przedmiot za dłonią, trzymając go prosto
  const el=this.held;
  if(!el)return;
  this.el.object3D.getWorldPosition(this.hand);
  this.el.object3D.getWorldQuaternion(this.quat);
  this.offset.set(this.data.holdOffset.x,this.data.holdOffset.y,this.data.holdOffset.z).applyQuaternion(this.quat);
  el.object3D.position.copy(this.hand).add(this.offset);
  el.object3D.rotation.set(0,0,0);
  el.object3D.updateMatrix();
 },
 tick(){if(this.held)this.follow();},
 moveTo(el,x,y,z){                              // zapis wprost do obiektu 3D i do atrybutu
  el.object3D.position.set(x,y,z);
  el.object3D.rotation.set(0,0,0);
  el.object3D.updateMatrix();
  el.setAttribute('position',x.toFixed(3)+' '+y.toFixed(3)+' '+z.toFixed(3));
  el.setAttribute('rotation','0 0 0');
 },
 size(el){
  const box=new THREE.Box3().setFromObject(el.object3D,true);
  if(!isFinite(box.min.x))return {radius:.2,height:.3};
  return {radius:Math.min(Math.max(box.max.x-box.min.x,box.max.z-box.min.z)/2,.32),
          height:Math.max(box.max.y-box.min.y,.05)};
 },
 body(){
  const el=document.querySelector('[player-body]');
  return el?el.components['player-body']:null;
 },
 place(el,point){                               // blat, siedzisko, parapet albo podłoga
  const collision=this.body();
  if(!collision)return {x:point.x,y:0,z:point.z};
  const size=this.size(el);
  const target=this.spotAt(collision,point.x,point.z,point.y,size);
  if(target)return target;
  const head=document.querySelector('#head'),headWorld=new THREE.Vector3();
  if(head)head.object3D.getWorldPosition(headWorld);
  const dx=headWorld.x-point.x,dz=headWorld.z-point.z,len=Math.hypot(dx,dz)||1;
  for(let i=1;i<=5;i++){                         // cofnij w stronę gracza, aż będzie wolne miejsce
   const back=i*0.15;
   const spot=this.spotAt(collision,point.x+dx/len*back,point.z+dz/len*back,point.y,size);
   if(spot)return spot;
  }
  const under=collision.support(headWorld.x,headWorld.z,size.radius,headWorld.y-1.0);
  const free=collision.free(headWorld.x,headWorld.z,under,size.height,size.radius);
  return {x:headWorld.x,y:free?under:0,z:headWorld.z};    // nie wkładaj przedmiotu w ścianę
 },
 spotAt(collision,x,z,fromY,size){
  const surface=collision.support(x,z,size.radius,fromY);
  return collision.free(x,z,surface,size.height,size.radius)?{x,y:surface,z}:null;
 },
 pick(){
  if(this.held)return;
  const el=this.target();
  if(!el)return;
  this.held=el;el.heldBy=this.el;
  this.follow();
  this.el.emit('grabbed',{object:el.id});
 },
 drop(){
  if(!this.held)return;
  const el=this.held,position=new THREE.Vector3();
  el.object3D.getWorldPosition(position);
  const spot=this.place(el,position);
  this.held=null;delete el.heldBy;
  this.moveTo(el,spot.x,spot.y,spot.z);
  this.el.emit('released',{object:el.id,x:spot.x,y:spot.y,z:spot.z});
 },
 remove(){
  this.el.removeEventListener('gripdown',this.onGripDown);
  this.el.removeEventListener('gripup',this.onGripUp);
 }
});
/* Left thumbstick: smooth movement in the direction the head looks, with collision
   against furniture and walls. A-Frame reports y>0 as stick-down, so forward is -y.
   Keyboard (W/A/S/D, arrows) drives the same movement for the desktop preview.
   Eye height is calibrated once per VR session so the room floor matches the user's
   floor; holding the stick clicked and pushing it up or down adjusts it and is saved. */
AFRAME.registerComponent('player-body',{
 schema:{speed:{default:1.4},radius:{default:.26},bodyHeight:{default:1.7},footClearance:{default:.15},minObstacleSize:{default:.06},minSupport:{default:.25},deadZone:{default:.15},invertForward:{default:false},eyeHeight:{default:1.8},sources:{default:'#model, #new-room'},dynamic:{default:'#door, #crate'}},
 init(){
  this.obstacles=[];this.dyn=[];this.stick={x:0,y:0};this.keys={};
  this.forward=new THREE.Vector3();this.right=new THREE.Vector3();this.headWorld=new THREE.Vector3();
  this.rig=document.querySelector('#rig');this.head=document.querySelector('#head');
  this.adjusting=false;this.calibrateAt=0;
  const saved=Number(localStorage.getItem('vrEyeHeight'));
  if(saved>0.8&&saved<2.6)this.data.eyeHeight=saved;
  this.onThumbstick=event=>{this.stick.x=event.detail.x||0;this.stick.y=event.detail.y||0;};
  this.onThumbstickDown=()=>{this.adjusting=true;};
  this.onThumbstickUp=()=>{this.adjusting=false;};
  this.onEnterVR=()=>{this.calibrateAt=performance.now()+900;};   // poczekaj, aż pozycja z gogli się ustali
  this.onKeyDown=event=>{this.keys[event.code]=true;};
  this.onKeyUp=event=>{this.keys[event.code]=false;};
  this.onLoaded=()=>this.buildObstacles();
  this.sources=[...document.querySelectorAll(this.data.sources)];
  this.dynamic=[...document.querySelectorAll(this.data.dynamic)];
  this.el.addEventListener('thumbstickmoved',this.onThumbstick);
  this.el.addEventListener('thumbstickdown',this.onThumbstickDown);
  this.el.addEventListener('thumbstickup',this.onThumbstickUp);
  window.addEventListener('keydown',this.onKeyDown);window.addEventListener('keyup',this.onKeyUp);
  if(this.el.sceneEl)this.el.sceneEl.addEventListener('enter-vr',this.onEnterVR);
  this.sources.forEach(el=>el.addEventListener('model-loaded',this.onLoaded));
  this.buildObstacles();
 },
 visible(node){                                  // ukryte meshe (stara ściana) nie tworzą kolizji
  let current=node;
  while(current){if(current.visible===false)return false;current=current.parent;}
  return true;
 },
 buildObstacles(){
  const box=new THREE.Box3(),list=[];
  const band=this.data;
  this.sources.forEach(entity=>{
   const root=entity.getObject3D('mesh');
   if(!root)return;
   root.updateMatrixWorld(true);
   root.traverse(node=>{
    if(!node.isMesh||!node.geometry||!this.visible(node))return;
    box.setFromObject(node,true);
    if(!isFinite(box.min.x)||!isFinite(box.max.x))return;
    if(box.max.y<=band.footClearance||box.min.y>=band.bodyHeight)return;             // podłoga, dywan, listwy, sufit
    if(box.max.x-box.min.x<band.minObstacleSize&&box.max.z-box.min.z<band.minObstacleSize)return;   // nogi, drobiazgi
    list.push({minX:box.min.x,maxX:box.max.x,minZ:box.min.z,maxZ:box.max.z,base:box.min.y,top:box.max.y});
   });
  });
  this.obstacles=list;
  if(this.el.sceneEl)this.el.sceneEl.emit('body-ready',{obstacles:list.length});
 },
 dynamicObstacles(){                             // drzwi i skrzynka zmieniają położenie
  const list=[],box=new THREE.Box3();
  this.dynamic.forEach(entity=>{
   if(!entity.object3D||!entity.getObject3D('mesh'))return;
   if(entity.heldBy)return;                                                          // trzymane w dłoni
   const door=entity.components['swing-door'];
   if(door&&door.open())return;                                                      // otwarte drzwi przepuszczają
   box.setFromObject(entity.object3D,true);
   if(!isFinite(box.min.x)||!isFinite(box.max.x))return;
   if(box.max.y<=this.data.footClearance||box.min.y>=this.data.bodyHeight)return;
   list.push({minX:box.min.x,maxX:box.max.x,minZ:box.min.z,maxZ:box.max.z,base:box.min.y,top:box.max.y});
  });
  return list;
 },
 /* Wsparcie i miejsce dla odkładanych przedmiotów (grab.place). */
 support(x,z,r,fromY){                           // najwyższa powierzchnia nie wyżej niż fromY
  let best=0;
  const limit=fromY+0.05;
  for(let i=0;i<this.obstacles.length;i++){
   const b=this.obstacles[i];
   if(b.maxX<x-r||b.minX>x+r||b.maxZ<z-r||b.minZ>z+r)continue;
   if(b.top<0.03||b.top>limit)continue;
   if(Math.min(b.maxX-b.minX,b.maxZ-b.minZ)<this.data.minSupport)continue;   // filiżanka, książka, ekran to nie blat
   if(b.top>best)best=b.top;
  }
  return best;
 },
 free(x,z,y,height,r){                           // czy przedmiot zmieści się na tej wysokości
  const rr=r*0.75,top=y+Math.max(height,0.05);
  for(let i=0;i<this.obstacles.length;i++){
   const b=this.obstacles[i];
   if(b.maxX<x-rr||b.minX>x+rr||b.maxZ<z-rr||b.minZ>z+rr)continue;
   if(b.top-b.base<0.12)continue;                // drobiazgi: książka, filiżanka, blat — nie przeszkadzają
   if(b.base>=top-0.01)continue;                 // mebel zaczyna się nad przedmiotem
   if(b.top<=y+0.02)continue;                    // mebel kończy się pod przedmiotem — to podpora
   return false;                                 // bryła przechodzi przez przedmiot
  }
  return true;
 },
 collides(x,z){
  const r=this.data.radius;
  for(let i=0;i<this.obstacles.length;i++){
   const o=this.obstacles[i];
   const cx=x<o.minX?o.minX:(x>o.maxX?o.maxX:x),cz=z<o.minZ?o.minZ:(z>o.maxZ?o.maxZ:z);
   const dx=x-cx,dz=z-cz;
   if(dx*dx+dz*dz<r*r)return true;
  }
  for(let i=0;i<this.dyn.length;i++){
   const o=this.dyn[i];
   const cx=x<o.minX?o.minX:(x>o.maxX?o.maxX:x),cz=z<o.minZ?o.minZ:(z>o.maxZ?o.maxZ:z);
   const dx=x-cx,dz=z-cz;
   if(dx*dx+dz*dz<r*r)return true;
  }
  return false;
 },
 eyeHeightNow(){                                 // wysokość oczu nad originem gogli przy rigu w y=0
  const v=new THREE.Vector3();
  this.head.object3D.getWorldPosition(v);
  return v.y-this.rig.object3D.position.y;
 },
 calibrate(){
  this.calibrateAt=0;
  const eye=this.eyeHeightNow();
  if(!(eye>0.4&&eye<2.4))return;                 // pozycja z gogli jeszcze nieustalona
  const offset=this.data.eyeHeight-eye;
  if(Math.abs(offset)<0.02)return;
  this.rig.object3D.position.y+=offset;
  this.el.emit('eye-height',{measured:+eye.toFixed(2),offset:+offset.toFixed(2)});
 },
 adjustHeight(delta){
  if(Math.abs(this.stick.y)<0.35)return;
  const change=-Math.sign(this.stick.y)*0.5*Math.min(delta/1000,.05);
  this.data.eyeHeight=Math.min(2.6,Math.max(0.9,this.data.eyeHeight+change));
  this.rig.object3D.position.y+=change;
  localStorage.setItem('vrEyeHeight',this.data.eyeHeight.toFixed(2));
 },
 input(){
  let sideways=this.adjusting?0:this.stick.x,forward=this.adjusting?0:(this.data.invertForward?this.stick.y:-this.stick.y);
  if(Math.abs(sideways)<this.data.deadZone)sideways=0;
  if(Math.abs(forward)<this.data.deadZone)forward=0;
  if(this.keys.KeyD||this.keys.ArrowRight)sideways+=1;
  if(this.keys.KeyA||this.keys.ArrowLeft)sideways-=1;
  if(this.keys.KeyW||this.keys.ArrowUp)forward+=1;
  if(this.keys.KeyS||this.keys.ArrowDown)forward-=1;
  return {sideways,forward};
 },
 tick(time,delta){
  if(this.calibrateAt&&performance.now()>=this.calibrateAt)this.calibrate();
  if(this.adjusting)this.adjustHeight(delta);
  this.dyn=this.dynamicObstacles();
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
  this.el.removeEventListener('thumbstickdown',this.onThumbstickDown);
  this.el.removeEventListener('thumbstickup',this.onThumbstickUp);
  window.removeEventListener('keydown',this.onKeyDown);window.removeEventListener('keyup',this.onKeyUp);
  this.sources.forEach(el=>el.removeEventListener('model-loaded',this.onLoaded));
  if(this.el.sceneEl)this.el.sceneEl.removeEventListener('enter-vr',this.onEnterVR);
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
  try{Promise.resolve(document.modelContext.registerTool({name:'move_to_room_view',description:'Przenieś widok do wejścia (0), okna (1), kanapy (2) lub pokoju za drzwiami (3).',inputSchema:{type:'object',properties:{index:{type:'integer',enum:[0,1,2,3]}},required:['index'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},execute(input){if(!Number.isInteger(input.index)||input.index<0||input.index>3)throw new Error('Nieznany punkt widokowy');goToView(input.index);return {index:input.index};}},{signal:lifecycle.signal})).catch(()=>{});}catch(e){}
  window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
 }
});
