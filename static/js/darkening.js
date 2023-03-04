var target_el_id = 0
var button_state = false


function updateButton()
{
    var submit_description_button = document.getElementById("description_commit_button")

    if (!button_state)
    {
        submit_description_button.innerHTML = "Commit"
        submit_description_button.classList.add("btn-primary")
        submit_description_button.classList.remove("btn-secondary")
    } else {
        submit_description_button.innerHTML = "Remove"
        submit_description_button.classList.add("btn-secondary")
        submit_description_button.classList.remove("btn-primary")
    }
}


function changeElement()
{
    var element_id = target_el_id
    button_state = !button_state
    document.getElementById("flexCheck_" + element_id).checked = button_state
    updateButton()
}


let elements_list = document.getElementsByClassName("darkening")

console.log(elements_list)

for (let i = 0; i < elements_list.length; i++)
{
    elements_list[i].onmouseover = function(event) {
        event.toElement.style.backgroundColor = "#e5e5e5";
        event.toElement.style.backgroundColor = "#e5e5e5";
    }
    elements_list[i].onmouseout = function(event) {
        event.fromElement.style.backgroundColor = "white";
    }
    elements_list[i].onclick = function(event) {
        var el = elements_list[i]
        target_el_id = el.id

        var descr_el = document.getElementById("description_id_" + el.id)

        let can_touch = (document.getElementById("day_can_touch_" + el.id).innerHTML == "True")

        button_state = document.getElementById("flexCheck_" + el.id).checked

        document.getElementById("description").innerHTML = descr_el.innerHTML
        document.getElementById("description_h").innerHTML = el.innerHTML + "Description"
        document.getElementById("description_commit_button").hidden = false

        var submit_description_button = document.getElementById("description_commit_button")
        submit_description_button.hidden = !can_touch
        updateButton()
        if (can_touch)
        {
            submit_description_button.onclick = changeElement
        }
    }
}