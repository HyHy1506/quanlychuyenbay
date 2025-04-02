const departureAirport= document.getElementById('departure_airport')
const arrivalAirport= document.getElementById('arrival_airport')
const timeStart= document.getElementById('time_start')
const ticketType= document.getElementById('ticket_type')

function searchFlight(){
    fetch('/api/flight_schedule/search', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "departure_airport_id": departureAirport.value.split(".")[0],
            "departure_airport_name": departureAirport.value.split(".")[1],
            "arrival_airport_id": arrivalAirport.value.split(".")[0],
            "arrival_airport_name": arrivalAirport.value.split(".")[1],
            "time_start": timeStart.value,
            "ticket_type": ticketType.value
        }),
    })
    .then(res=>res.json())
    .then(data=>{
         window.location.href = '/flight-list'
    }).catch(err=>{
        console.error(err)
    })
}