(() => {
  const form = document.querySelector("#demo-booking");
  if (!form) return;
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
  }
  form.querySelectorAll('p').forEach(p=>{if(p.textContent.includes("свободных часов нет"))p.remove()});
  form.querySelector('[name="birth_date"]').max=iso(today);
  form.addEventListener("submit",e=>{
    e.preventDefault();
    const time=new FormData(form).get("visit_time");
    if(!time||!slots.includes(time)||new Date(selected+"T"+time)<=new Date()||occupied(selected,time)){render();alert("Выберите доступное время.");return}
    try{localStorage.setItem(key,JSON.stringify([...read(),[form.dataset.doctor,selected,time].join("|")]))}catch{alert("Браузер не разрешил сохранить демонстрационную запись.");return}
    form.reset();render();
    const result=document.createElement("div");result.className="panel";result.setAttribute("role","status");result.textContent="Демонстрационная запись подтверждена: "+display(selected)+" в "+time+". Персональные данные не сохранены.";
    form.prepend(result);result.scrollIntoView({behavior:"smooth"});
  });
  window.addEventListener("storage",e=>{if(e.key===key)render()});
  render();
})();