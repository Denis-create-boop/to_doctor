(() => {
 const input=document.querySelector('input[name="snils"]');
 if(!input)return;
 function format(value){
  const d=value.replace(/[^0-9]/g,"").slice(0,11);
  return d.slice(0,3)+(d.length>3?"-"+d.slice(3,6):"")+(d.length>6?"-"+d.slice(6,9):"")+(d.length>9?" "+d.slice(9,11):"");
 }
 input.addEventListener("input",()=>{
  const raw=input.value, pos=input.selectionStart??raw.length;
  const count=raw.slice(0,pos).replace(/[^0-9]/g,"").length;
  input.value=format(raw);
  let cursor=0, seen=0;
  while(cursor<input.value.length&&seen<count){if(/[0-9]/.test(input.value[cursor]))seen++;cursor++;}
  input.setSelectionRange(cursor,cursor);
 });
 input.addEventListener("keydown",e=>{
  const p=input.selectionStart;
  if(e.key==="Backspace"&&p===input.selectionEnd&&p>0&&/[- ]/.test(input.value[p-1])){
   e.preventDefault();input.value=format(input.value.slice(0,p-2)+input.value.slice(p));input.setSelectionRange(p-2,p-2);
  }
 });
 input.value=format(input.value);
})();