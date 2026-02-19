document.addEventListener("DOMContentLoaded", function ()
{
    createHistory();
});

function createHistory()
{
    const dummyAmpel = document.getElementById("dummy-ampel");
    const displayContainer = document.getElementById("display-container");

    var headers = {
        "Access-Control-Origin": "*",
    }

    fetch('/api/history', {
        method: 'get',
        headers: headers,
    }).then((response) =>
    {
        if (response.ok) return response.json();
        throw new Error("Error: " + response.status);
    }).then((responseJSON) =>
    {
        document.getElementById("history-title").textContent = `Verlauf zwischen ${responseJSON[0][1]} und ${responseJSON[responseJSON.length - 1][1]}`

        var min = 5;
        var minDate = "";
        var max = -1;
        var maxDate = "";

        for (const entry of responseJSON.reverse())
        {
            var level = level = Math.min(Math.max(entry[0], 0), 4);;
            if (level < min)
            {
                min = level;
                minDate = entry[1];
            }
            if (level > max)
            {
                max = level;
                maxDate = entry[1];
            }

            var div = document.createElement("div");
            div.classList.add("history-entry");
            var img = document.createElement("img");
            img.src = `/static/img/ampel${level}.svg`;
            div.appendChild(img);
            var caption = document.createElement("span");
            caption.classList.add("caption");
            caption.innerText = entry[1];
            div.appendChild(caption);
            displayContainer.appendChild(div);
        }

        document.getElementById("min-field").innerHTML = `${min}&emsp;(${minDate})`;
        document.getElementById("max-field").innerHTML = `${max}&emsp;(${maxDate})`;
    }).catch((error) =>
    {
        console.log(error);
    });
}