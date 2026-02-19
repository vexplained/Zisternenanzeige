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
        let filllevel = responseJSON["filllevel"];
        let timeOfReading = responseJSON["timeOfReading"];
        if (timeOfReading == undefined) timeOfReading = "---";
        document.getElementById("refresh-date").textContent = timeOfReading;

        let classList = document.getElementById("ampel-img").classList;
        classList.remove("filllevel0");
        classList.remove("filllevel1");
        classList.remove("filllevel2");
        classList.remove("filllevel3");
        classList.remove("filllevel4");

        classList.add(`filllevel${filllevel}`)

    }).catch((error) =>
    {
        console.log(error);
    });
}