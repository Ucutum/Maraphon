const TASKS_ID = Array.from(
    document.getElementsByClassName("day")).map(x => x.textContent)
console.log(TASKS_ID)


function updateStatusbar()
{
    done = 0
    notdone = 0
    nowdone = 0
    nownotdone = 0
    undone = 0
    TASKS_ID.forEach(function(id)
    {
        e = document.getElementById("flexCheck_" + id)
        checked = e.checked
        disabled = e.disabled
        if (disabled)
        {
            date = new Date(document.getElementById("date_" + id).innerHTML)
            if (date < new Date())
            {
                if (checked)
                {
                    done += 1
                }
                else
                {
                    notdone += 1
                }
            }
            else
            {
                undone += 1
            }
        }
        else
        {
            if (checked)
            {
                nowdone += 1
            }
            else
            {
                nownotdone += 1
            }
        }
    })

    all = done + notdone + nowdone + nownotdone + undone

    p = (done * 100) / all
    document.getElementById("done_bar")["aria-valuenow"] = p
    document.getElementById("done_bar").style = "width: " + p.toString() + "%"

    p = (notdone * 100) / all
    document.getElementById("notdone_bar")["aria-valuenow"] = p
    document.getElementById("notdone_bar").style = "width: " + p.toString() + "%"

    p = (nowdone * 100) / all
    document.getElementById("nowdone_bar")["aria-valuenow"] = p
    document.getElementById("nowdone_bar").style = "width: " + p.toString() + "%"

    p = (nownotdone * 100) / all
    document.getElementById("nownotdone_bar")["aria-valuenow"] = p
    document.getElementById("nownotdone_bar").style = "width: " + p.toString() + "%"
}