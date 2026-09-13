/* World positions in metres. Teleport uses the tracked head offset. */
const viewpoints = [{x:0,z:1.05,yaw:0},{x:-1.5,z:0,yaw:-70},{x:.85,z:-.65,yaw:180}];
function goToView(index){
 const target=viewpoints[index],rig=document.querySelector('#rig'),head=document.querySelector('#head');
 if(!target||!rig||!head)return;
 const world=new THREE.Vector3();head.object3D.getWorldPosition(world);
 rig.object3D.position.x+=target.x-world.x;rig.object3D.position.z+=target.z-world.z;
 if(!rig.sceneEl.is('vr-mode')){rig.object3D.rotation.y=THREE.MathUtils.degToRad(target.yaw);head.components['look-controls'].yawObject.rotation.y=0;head.components['look-controls'].pitchObject.rotation.x=0;}
}
AFRAME.registerComponent('teleport-to',{schema:{index:{type:'int'}},init(){this.el.addEventListener('click',()=>goToView(this.data.index));}});
AFRAME.registerComponent('snap-turn',{init(){
 this.ready=true;this.el.addEventListener('thumbstickmoved',event=>{
 const x=event.detail.x;if(Math.abs(x)<.25)this.ready=true;
 if(!this.ready||Math.abs(x)<.75)return;this.ready=false;
 const rig=document.querySelector('#rig').object3D,head=document.querySelector('#head').object3D;
 const before=new THREE.Vector3(),after=new THREE.Vector3();head.getWorldPosition(before);
 rig.rotation.y-=Math.sign(x)*Math.PI/6;rig.updateMatrixWorld(true);head.getWorldPosition(after);
 rig.position.x+=before.x-after.x;rig.position.z+=before.z-after.z;
 });
}});
window.addEventListener('DOMContentLoaded',()=>{
 const scene=document.querySelector('a-scene'),model=document.querySelector('#model'),status=document.querySelector('#status'),button=document.querySelector('#enter');
 model.addEventListener('model-loaded',async()=>{status.textContent='Pokój gotowy. Rozejrzyj się.';
 try{if(navigator.xr&&await navigator.xr.isSessionSupported('immersive-vr')){button.disabled=false;}else{button.textContent='Otwórz tę stronę w Quest';}}catch(e){status.textContent='Podgląd 3D gotowy. VR wymaga przeglądarki Quest i HTTPS.';}
 });
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
