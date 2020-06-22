console.log('main.js loaded successfully!')

msgCount = 0;
function create_messages(messages, doScroll = false, clear=true) {
  if (clear) $("#div_messages2").html("");

  $.each(messages, function (i, m) {
    const msgHtml = /*html*/ `
      <div class="d-flex justify-content-between alert alert-${m.tag} shadow-sm alert-dismissable">
        <div>${m.message}</div>
        <div><a href="#" class="close align-top" data-dismiss="alert" aria-label="close">×</a></div>
      </div>
    `;
    $(msgHtml).attr("id","msg"+msgCount).appendTo($("#div_messages2")).hide().fadeIn("fast");
    if (doScroll) {
      document.getElementById("msg"+msgCount).scrollIntoView({ behavior: 'smooth', block: 'start'});
    }
    msgCount++;
  });
}


var lastCityId = 'cityRow0'
var cityArray = []
cityArray[0] ='cityRow0'

var maxCityCount = 5

for (let i = 1; i < maxCityCount; i++) {
  cityArray.push('')
}

var cityCount = 1

var currId = 1

function addCity() {
  if (cityCount < maxCityCount) {
    //console.log('Adding new city, current count is - ' + cityCount)

    //Находим первую пустую строку в массиве
    currId = cityArray.findIndex(function(element, index, array) {
      if (element == '') {
        return true
      } else return false
    })

    //Запишем айди предыдущего элемента
    lastCityId = cityArray[currId-1]

    let id = "cityRow" + currId;
    let name = "city" + currId;

    //Создаём клона и записываем его в переменную clone
    let clone = $('#'+lastCityId).clone().attr({'id':id})
    clone.find("input").attr({'id':'inputCity'+currId,'name':name}).val('');
    clone.find("button").attr({'id':'delbutton'+currId,'onclick':'delCity("'+id+'")'}).removeAttr("hidden")
    //Вставляем его в HTML документ
    clone.insertAfter($('#'+lastCityId)).hide().slideDown("fast")
    // console.log(clone.find("input"))
    //Обновим массив, добавив айди нового эелемента под своим порядковым номером
    cityArray[currId] = id
    console.log(cityArray)

    cityCount++
    currId++

    cityCount == maxCityCount ? $('#addbutton').slideUp("fast") : null
  } else {
    console.log('Reached maximum');
  }
};

function delCity(id) {
  let num = id.slice(-1)
  console.log('Removing city ' + id + ', number is - ' + num)
  
  let el = $('#'+id)
  el.slideUp("fast", function() {  
      el.remove()
    }
  )

  $('#addbutton').slideDown("fast");

  cityArray[num] = ''
  lastCityId = lastCityId.slice(0,-1) + (num-1)
  currId = num
  cityCount--

  console.log('Last city ID is now - '+ lastCityId)
  console.log(cityArray)
}


function addCars(carsArray, clear=true) {
  if (clear) $("#cont").html("");
  console.log('Adding cars...')
  for (let i=0; i < carsArray.length; i++) {
    let newCar = $("#refCarCard").clone().attr({'id':'car'+i})
    newCar.appendTo($("#cont")).addClass('carel')
  }
}

function loadCar(resultCard) {
  let i = resultCard.attr('id')
  if (!resultCard.attr('isloaded')) {
    console.log('loading')
    let el = window.lastResult[i.slice(3,i.length)]

    //let resultCard = $("#refCarCard").clone().attr('href',el.url)
    resultCard.attr('href',el.url).css('visibility','visible')
    resultCard.find('#ctitle').text(el.title)
    resultCard.find('#cprice').text(el.price.toLocaleString()+' ₽')
    try {
      resultCard.find('#cyear').text(`Год выпуска: ${el.year}`)
    } catch{ }
    resultCard.find('#csite').text(`Источник: ${el.site}`)
    resultCard.find('#img_url').attr('src',el.img)
    let cdatetmp = el.dtime_as_TZ.substring(0,10).split('-')
    cdate = [cdatetmp[2],cdatetmp[1],cdatetmp[0]].join('.')
    let t = el.dtime_as_TZ.substring(11,19)
    //console.log(el.dtime_as_TZ)
    resultCard.find('#ctime').text(`Найдено ${cdate} в ${t}`)

    resultCard.hide().fadeIn()

    resultCard.attr('isloaded','yes')
  }
}

function sendFilter(token, type=null) {
  console.log('Send button clicked')
  let timeStart = Date.now();
  let url_t = '/result/'

  BtnSendingState()

  document.getElementById("cityCount").setAttribute("value", cityCount)

  var form = $("#send")

  let formSerialized = form.serialize()
  console.log(formSerialized)
  console.log(typeof(type))
  if (type == 'other'){
    url_t = '/result_other/'
    console.log(url_t)
  }

  $.ajax({
    headers: {
      "X-CSRFToken": token
    },
    method: "POST",
    url: url_t,
    data: formSerialized,
    dataType: 'json',
    success: function (data) {
      console.log('Recieved! Success is - ' + data.success + ', response code is - ' + data.code);
      //console.log(`Cars array length is - ${Object.keys(data.cars).length}`)
      BtnSendingState(false)

      create_messages(data.messages);

      if (data.success) {
        //data.cars = JSON.parse(data.cars)
        //console.log(typeof(data.cars))
        console.log(data.cars)
        window.lastResult = data.cars
        addCars(data.cars);
        document.getElementById("div_messages2").scrollIntoView({ behavior: 'smooth', block: 'start'})
        console.log("Time spent: ",(Date.now()-timeStart)/1000);

      } else {
        console.log('Server returned error - no cars gathered!')
        create_messages(data.messages, true);
      }
    },
    error: function (jqXHR, exception){
      console.log("Send button action failed!", jqXHR, exception)
      create_messages([{
        'tag':'danger',
        'message':`Во время отправки произошла ошибка. Пожалуйста, попробуйте ещё раз позже.
        Ошибка: <br>
        ${jqXHR.responseText.substring(0, jqXHR.responseText.indexOf(":") + 6)}`
      }], true);
      BtnSendingState(false)
    }
  })
};


function BtnSendingState(bool = true) {
  if (bool) {
    button = $("#sendBtn")
    button.attr("disabled", "true")
    button.children("#sendText").text("Загрузка...")
    button.children("#sendSpinner").show("fast")
  } else {
    button.removeAttr("disabled")
    button.children("#sendText").text("Отправить")
    button.children("#sendSpinner").hide("fast")
  }
}



$(document).ready(function() {

  /* Every time the window is scrolled ... */
  $(window).scroll( function(){
  
      /* Check the location of each desired element */
      $('.carel').each( function(i){
  
          var bottom_of_object = $(this).position().top + $(this).outerHeight();
          var bottom_of_window = $(window).scrollTop() + $(window).height();
  
          /* If the object is completely visible in the window, fade it in */
          if( bottom_of_window > bottom_of_object ){
  
              //$(this).animate({'opacity':'1'},500);
              loadCar($(this))
          }    
      }); 
  }); 
});