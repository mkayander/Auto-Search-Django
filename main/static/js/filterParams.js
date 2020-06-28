$(document).ready(function() {
    //console.log(document.querySelector('#mainPanel'))
    //console.log(document.getElementById('savedfilter-data'))
    var filter = JSON.parse(document.getElementById('savedfilter-data').textContent)
    console.log(filter)
    if (filter){
        document.getElementById('inputCity0').value = filter.cities
        $(`#carname_mark option[value="${filter.carname_mark}"]`).prop('selected',true)
        $(`#carname_model option[value="${filter.carname_model}"]`).prop('selected',true)
        $(`#hull option[value="${filter.hull}"]`).prop('selected',true)
        $(`#fuel option[value="${filter.fuel}"]`).prop('selected',true)
        $(`#transm option[value="${filter.transm}"]`).prop('selected',true)
        $(`#radius option[value="${filter.radius}"]`).prop('selected',true)
        document.getElementById('price_from').value = filter.price_from
        document.getElementById('price_to').value = filter.price_to
        $(`#year_from option[value="${filter.year_from}"]`).prop('selected',true)
        $(`#year_to option[value="${filter.year_to}"]`).prop('selected',true)
        $(`#engine_from option[value="${filter.engine_from}"]`).prop('selected',true)
        $(`#engine_to option[value="${filter.engine_to}"]`).prop('selected',true)

        let btn = document.getElementById('sendBtn')
        btn.innerText = "Сохранить"
        btn.removeAttribute("onclick")
        btn.type = "submit"
    }
})



// window.onload = function() {
//     var filter = JSON.parse(document.getElementById('savedfilter-data').textContent)
//     $(`#carname_model option[value="${filter.carname_model}"]`).prop('selected',true)
//     console.log($(`#carname_model option[value="${filter.carname_model}"]`))
// }