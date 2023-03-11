var target_el_id = 0


function updateButton(state)
{
    var submit_description_button = document.getElementById("description_commit_button")

    if (!state)
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
    document.getElementById("flexCheck_" + target_el_id).checked = ! document.getElementById("flexCheck_" + target_el_id).checked
    Check(target_el_id)
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

        console.log("target el id: " + target_el_id)

        var descr_el = document.getElementById("description_id_" + el.id)

        let can_touch = (document.getElementById("day_can_touch_" + el.id).innerHTML == "True")

        document.getElementById("description").innerHTML = descr_el.innerHTML
        document.getElementById("description_h").innerHTML = el.innerHTML + "Description"
        document.getElementById("description_commit_button").hidden = false
        document.getElementById("description_date").innerHTML = document.getElementById("date_" + el.id).innerHTML
        document.getElementById("description_done_users").innerHTML = document.getElementById("done_users_" + el.id).innerHTML

        var submit_description_button = document.getElementById("description_commit_button")
        submit_description_button.hidden = !can_touch
        updateButton(document.getElementById("flexCheck_" + el.id).checked)
        if (can_touch)
        {
            submit_description_button.onclick = changeElement
        }
    }
}