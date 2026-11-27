(async()=>{
 const $=id=>document.getElementById(id);
 let params=new URLSearchParams(location.search);
 try{if(!params.has("doctor"))params=new URLSearchParams(localStorage.getItem("medika-demo-last-v1")||"")}catch{}
 const id=params.get("doctor"),date=params.get("date"),time=params.get("time");
 const empty=()=>{$("receipt-title").textContent="Запись не найдена";$("receipt-check").textContent="!";$("receipt-note").textContent="Выберите врача и оформите запись на приём.";};
 try{
  const reserved=JSON.parse(localStorage.getItem("medika-demo-slots-v1")||"[]");
  if(!reserved.includes([id,date,time].join("|"))||!/^\d{4}-\d{2}-\d{2}$/.test(date||"")||!/^\d{2}:\d{2}$/.test(time||""))return empty();
  const response=await fetch("/to_doctor/static/demo_doctors.json");
  if(!response.ok)throw Error("catalog");
  const catalog=await response.json(),doctor=catalog[id];
  if(!doctor)return empty();
  $("receipt-title").textContent="Вы записаны на приём!";
  $("receipt-note").textContent="Демонстрационная запись сохранена в этом браузере.";
  $("receipt-doctor").textContent=doctor.name;
  $("receipt-specialty").textContent=doctor.specialty;
  $("receipt-date").textContent=date.split("-").reverse().join(".");
  $("receipt-time").textContent=time;
  $("receipt-details").hidden=false;
 }catch{$("receipt-title").textContent="Не удалось открыть запись";$("receipt-note").textContent="Обновите страницу или проверьте настройки браузера."}
})();