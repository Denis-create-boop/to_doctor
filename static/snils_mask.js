(() => {
 const input=document.querySelector('input[name="snils"]');
 if(!input)return;
 const pattern="___-___-___ __";
 const slots=[0,1,2,4,5,6,8,9,10,12,13];
 const digits=value=>value.replace(/[^0-9]/g,"").slice(0,11);
 const format=value=>{const d=digits(value);return [...pattern].map((c,i)=>c==="_"?(d[slots.indexOf(i)]||"_"):c).join("");};
 const wrapper=document.createElement("div");wrapper.className="snils-mask-wrap";
 input.before(wrapper);wrapper.append(input);
 const guide=document.createElement("span");guide.className="snils-mask-guide";guide.setAttribute("aria-hidden","true");wrapper.append(guide);
 input.maxLength=14;input.placeholder="";input.autocomplete="off";
 function refresh(){
  const d=digits(input.value);
  const formatted=format(d);
  guide.replaceChildren();
  const entered=document.createElement("span");entered.className="snils-entered";
  const remaining=document.createElement("span");
  const boundary=d.length===11?14:slots[d.length];
  entered.textContent=formatted.slice(0,boundary);
  remaining.textContent=formatted.slice(boundary);
  guide.append(entered,remaining);
 }
 function formatInput(){
  const raw=input.value,pos=input.selectionStart??raw.length;
  const count=Math.min(11, digits(raw.slice(0,pos)).length);
  const d=digits(raw);
  input.value=format(d).split("_")[0].replace(/[- ]$/,"");
  let cursor=0,seen=0;
  while(cursor<input.value.length&&seen<count){if(/[0-9]/.test(input.value[cursor]))seen++;cursor++;}
  input.setSelectionRange(cursor,cursor);refresh();
 }
 input.addEventListener("input",formatInput);
 input.addEventListener("beforeinput",e=>{
  if(e.inputType==="insertText"&&e.data){
   const selected=input.value.slice(input.selectionStart,input.selectionEnd);
   if(!/^[0-9]+$/.test(e.data)||digits(input.value).length-digits(selected).length+e.data.length>11)e.preventDefault();
  }
 });
 input.addEventListener("keydown",e=>{
  const p=input.selectionStart;
  if(e.key==="Backspace"&&p===input.selectionEnd&&p>1&&/[- ]/.test(input.value[p-1])){
   e.preventDefault();input.value=input.value.slice(0,p-2)+input.value.slice(p);input.setSelectionRange(p-2,p-2);formatInput();
  }
 });
 input.form?.addEventListener("reset",()=>setTimeout(refresh,0));
 formatInput();
})();