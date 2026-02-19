document.addEventListener("DOMContentLoaded", function ()
{
    updateMeter(false);

    // Using JS instead of plain HTML to prevent the site from reloading when POSTing
    const button = document.getElementById('btn-refresh');

    button.addEventListener('click', async _ =>
    {
        updateMeter(true);
    });
});

function updateMeter(forceRefresh)
{
    var headers = {
        "Access-Control-Origin": "*",
        "Content-Type": "application/json",
    }

    fetch('/api/sensors', {
        method: 'post',
        headers: headers,
        body: JSON.stringify({ "refreshReadings": forceRefresh.toString() }),
    }).then((response) =>
    {
        if (response.ok) return response.json();
        throw new Error("Error: " + response.status);
    }).then((responseJSON) =>
    {
	document.getElementById("img-ampel").remove();
        let level = responseJSON["filllevel"];
        let img = document.createElement("img");
	img.id = "img-ampel";
        img.src = `/static/img/ampel${level}.svg`;
        document.getElementById("display-container").append(img);
        let timeOfReading = responseJSON["timeOfReading"];
        if (timeOfReading == undefined) timeOfReading = "---";
        document.getElementById("refresh-date").textContent = timeOfReading;

    }).catch((error) =>
    {
        console.log(error);
    });
}
