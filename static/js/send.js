function Check(id)
{
    Check_(id)
    updateStatusbar()
}


async function Check_(id)
{
    var xhr = new XMLHttpRequest()
    xhr.open("POST", "/state/" + id, true)

    xhr.onload = function() {
        console.log(`Загружено: ${xhr.status} ${xhr.response}`);
        state = JSON.parse(xhr.response).state
        console.log(state)
        updateButton(state)
        document.getElementById("flexCheck_" + id).checked = state
    };
    
    xhr.onerror = function() { // происходит, только когда запрос совсем не получилось выполнить
        console.log(`Ошибка соединения. Status: ${xhr.status}`);
    };
    
    xhr.onprogress = function(event) { // запускается периодически
        // event.loaded - количество загруженных байт
        // event.lengthComputable = равно true, если сервер присылает заголовок Content-Length
        // event.total - количество байт всего (только если lengthComputable равно true)
        console.log(`Загружено ${event.loaded} из ${event.total}`);
    };

    send_state = document.getElementById("flexCheck_" + id).checked
    data = JSON.stringify({state: send_state})
    console.log(send_state, data)
    return xhr.send(data)
}

var tasks = Array.from(document.getElementsByClassName("day"))
console.log(tasks)
tasks.forEach(function(e){
    Check(e.textContent)
})