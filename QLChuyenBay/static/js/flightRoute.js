const btnSubmit= document.querySelector('.btn-submit')
const inp_da= document.getElementById('departure')
const inp_aa= document.getElementById('arrival')

function addRoute(){
    fetch('/api/admin-route-flight', {
        method: "POST",
        body: JSON.stringify({
            "depart_airport": inp_da.value,
            "arrival_airport": inp_aa.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res=>res.json())
    .then(data=>{
        if(data.status==200){
            Swal.fire({
              position: "top-end",
              icon: "success",
              title: "Bạn đã lưu thành công!",
              showConfirmButton: false,
              timer: 1500});
            location.reload()
        }
        if(data.status==500){
            Swal.fire("Lỗi", "Tuyến bay đã tồn tại! Vui lòng chọn tuyến khác!", "error")
        }
    }).catch(err=>{
        console.error(err)
    })
}

function deleteRoute(id){
    return Swal.fire({
          title: "Bạn có chắc chắn muốn xóa tuyến bay này?",
          text: "Không thể hoàn tác!",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#3085d6",
          cancelButtonColor: "#d33",
          confirmButtonText: "OK!"
    }).then((result) => {
    if (result.isConfirmed) {
        fetch(`/api/delete-route/${id}`, {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
             const routeElement = document.getElementById(`route${id}`);
             if (routeElement) {
                routeElement.style.display = "none";
             } else {
                console.warn("Element with id route", id, "not found");
             }
        })
        .catch(err => {
             console.error("Error deleting route:", err);
        });
            Swal.fire({
                title: "Đã xóa!",
                text: "Tuyến bay này đã được xóa.",
                icon: "success"
            });
        }
    })
}
