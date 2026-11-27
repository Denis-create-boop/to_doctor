(() => {
  const form = document.querySelector("#demo-booking");
  if (!form) return;
  form.noValidate=true;
  const key = "medika-demo-slots-v1";
  const dates = document.querySelector(".date-grid"), times = document.querySelector(".time-grid");
  const dayInput = form.querySelector('[name="day"]'), submit = form.querySelector("button");
  const heading = times.previousElementSibling.previousElementSibling;
  const summary = document.querySelector(".summary");
  const today = new Date(); today.setHours(0,0,0,0);
  const iso = d => [d.getFullYear(),String(d.getMonth()+1).padStart(2,"0"),String(d.getDate()).padStart(2,"0")].join("-");
  const display = d => d.split("-").reverse().join(".");
  const slots = Array.from({length:9},(_,i)=>String(8+Math.floor(i/2)).padStart(2,"0")+":"+(i%2?"30":"00"));
  let selected = iso(today);
  const read = () => {try {const value=JSON.parse(localStorage.getItem(key)||"[]");return Array.isArray(value)?value:[]}catch{return []}};
  const occupied = (day,time) => read().includes([form.dataset.doctor,day,time].join("|"));
  function render(){
    dayInput.value=selected;
    dates.replaceChildren();
    for(let i=0;i<30;i++){
      const d=new Date(today);d.setDate(d.getDate()+i);
      const a=document.createElement("a"); a.href="#";a.className="day"+(iso(d)===selected?" active":"");
      for(const [tag,value] of [["small",d.toLocaleDateString("ru-RU",{weekday:"short"})],["strong",d.getDate()],["small",d.toLocaleDateString("ru-RU",{month:"short"})]]){const e=document.createElement(tag);e.textContent=value;a.append(e)}
      a.onclick=e=>{e.preventDefault();selected=iso(d);render()};dates.append(a);
    }
    if(heading)heading.textContent="2. Время · "+display(selected);
    const summaryDate=summary.querySelector("hr")?.nextElementSibling;
    if(summaryDate){summaryDate.replaceChildren();const b=document.createElement("b");b.textContent="Дата";summaryDate.append(b,document.createElement("br"),display(selected))}
    times.replaceChildren();let count=0;
    for(const t of slots){
      const taken=occupied(selected,t), past=new Date(selected+"T"+t)<=new Date();
      const l=document.createElement("label");l.className="time"+(taken||past?" unavailable":"");
      const input=document.createElement("input");input.type="radio";input.name="visit_time";input.value=t;input.required=true;input.disabled=taken||past;
      const span=document.createElement("span"),small=document.createElement("small");span.textContent=t;small.textContent=taken?"Занято":past?"Прошло":"Свободно";span.append(small);l.append(input,span);times.append(l);if(!input.disabled)count++;
    }
    submit.disabled=!count;
    const available=times.querySelector("input:not(:disabled)");
    if(available)available.checked=true;
  }
  form.querySelectorAll('p').forEach(p=>{if(p.textContent.includes("свободных часов нет"))p.remove()});
  form.querySelector('[name="birth_date"]').max=iso(today);
  const error=document.createElement("div");error.className="error";error.hidden=true;error.setAttribute("role","alert");submit.before(error);
  function fail(message){error.textContent=message;error.hidden=false;error.scrollIntoView({block:"nearest"});}
  form.addEventListener("submit",e=>{
    e.preventDefault();
    error.hidden=true;
    const data=new FormData(form);
    const name=String(data.get("patient_name")||"").trim();
    const birth=String(data.get("birth_date")||"");
    if(name.length<3||name.length>120)return fail("Введите ФИО пациента.");
    if(!birth||birth<"1900-01-01"||birth>iso(today))return fail("Укажите корректную дату рождения.");
    const digits=String(data.get("snils")||"").replace(/[ -]/g,"");
    if(!/^\d{11}$/.test(digits)){fail("Введите СНИЛС: 11 цифр.");return}
    const time=data.get("visit_time");
    if(!time||!slots.includes(time)||new Date(selected+"T"+time)<=new Date()||occupied(selected,time)){fail("Выберите доступное время приёма, нажав на нужную ячейку.");return}
    try{localStorage.setItem(key,JSON.stringify([...read(),[form.dataset.doctor,selected,time].join("|")]))}catch{fail("Браузер не разрешил сохранить демонстрационную запись.");return}
    const receipt={doctor:summary.querySelector("h2").textContent.trim(),specialty:summary.querySelector("p").textContent.trim(),date:selected,time};
    const params=new URLSearchParams({doctor:form.dataset.doctor,date:selected,time});
    // No patient name, SNILS or birth date is stored or included in the URL.
    try{localStorage.setItem("medika-demo-last-v1",params.toString())}catch{}
    form.reset();
    const modal=document.createElement("dialog");
    modal.className="panel success";
    modal.style.cssText="max-width:min(92vw,480px);border:0;border-radius:20px;padding:32px;text-align:center;color:#173c38";
    const check=document.createElement("div");check.className="check";check.textContent="✓";
    const title=document.createElement("h2");title.textContent="Вы успешно записаны на приём!";
    const detail=document.createElement("p");detail.textContent=receipt.doctor+" · "+display(selected)+" в "+time;
    const next=document.createElement("button");next.type="button";next.className="button";next.textContent="Посмотреть запись";
    const openReceipt=()=>location.assign("/to_doctor/confirmation/?"+params.toString());
    next.onclick=openReceipt;
    modal.addEventListener("cancel",e=>{e.preventDefault();openReceipt()});
    modal.append(check,title,detail,next);document.body.append(modal);
    modal.classList.add("booking-confirm-dialog");
    if(typeof modal.showModal==="function"){try{modal.showModal();next.focus()}catch{openReceipt()}}else{openReceipt()}
  });
  window.addEventListener("storage",e=>{if(e.key===key)render()});
  render();
})();