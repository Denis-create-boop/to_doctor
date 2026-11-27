(() => {
 const input=document.querySelector('input[name="snils"]');
 if(!input)return;
 const positions=[0,1,2,4,5,6,8,9,10,12,13];
 const clean=v=>v.replace(/[^0-9]/g,"").slice(0,11);
 let digits=clean(input.value);
 const hidden=document.createElement("input");
 hidden.type="hidden";hidden.name="snils";
 input.name="snils_display";input.id="snils-display";
 input.removeAttribute("required");input.maxLength=14;
 input.after(hidden);
 const index=pos=>positions.filter(p=>p<pos).length;
 function render(caret=digits.length){
  const padded=digits.padEnd(11,"0");
  input.value=padded.slice(0,3)+"-"+padded.slice(3,6)+"-"+padded.slice(6,9)+"-"+padded.slice(9);
  hidden.value=digits;
  input.dataset.filled=String(digits.length);
  input.setCustomValidity(digits.length===11?"":"Введите 11 цифр СНИЛС.");
  input.style.color=digits.length?"":"#869c96";
  const p=positions[Math.min(caret,11)]??14;
  input.setSelectionRange(p,p);
 }
 function edit(value,back=false,forward=false){
  let a=Math.min(index(input.selectionStart??0),digits.length);
  let b=Math.min(index(input.selectionEnd??0),digits.length);
  if(back&&a===b)a=Math.max(0,a-1);
  if(forward&&a===b)b=Math.min(digits.length,b+1);
  const added=clean(value).slice(0,11-digits.length+b-a);
  digits=digits.slice(0,a)+added+digits.slice(b);
  render(a+added.length);
 }
 input.addEventListener("beforeinput",e=>{
  if(e.inputType.startsWith("insert")&&e.data!==null){
   e.preventDefault();edit(e.data);
  }else if(e.inputType==="deleteContentBackward"||e.inputType==="deleteContentForward"){
   e.preventDefault();edit("",e.inputType==="deleteContentBackward",e.inputType==="deleteContentForward");
  }
 });
 input.addEventListener("paste",e=>{e.preventDefault();edit(e.clipboardData.getData("text"));});
 input.addEventListener("input",()=>{digits=clean(input.value);render();});
 input.addEventListener("focus",()=>{if(!digits.length)input.setSelectionRange(0,0);});
 input.addEventListener("click",()=>{if(index(input.selectionStart)>digits.length)render();});
 input.form?.addEventListener("reset",()=>setTimeout(()=>{digits="";render();},0));
 render();
})();