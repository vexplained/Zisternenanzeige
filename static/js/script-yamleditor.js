document.addEventListener("DOMContentLoaded", function ()
{
    const yamlEditor = document.getElementById("yamlEditor");
    const saveButton = document.getElementById("saveButton");
    const messageElement = document.getElementById("message");


    function showMessage(status, text)
    {
        messageElement.innerHTML = text;
        messageElement.classList.add(status);
        setTimeout(function ()
        {
            messageElement.innerHTML = "";
            messageElement.classList.remove(status);
        }, status == "success" ? 3000 : 15000);
    }

    fetch("/api/config")
        .then((response) => response.text())
        .then((data) =>
        {
            yamlEditor.value = data;
        });

    saveButton.addEventListener("click", function ()
    {
        const yamlData = yamlEditor.value;
        fetch("/api/config", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-yaml",
            },
            body: yamlData,
        })
            .then((response) => response.json())
            .then((data) =>
            {
                if (data.status === "success")
                {
                    showMessage("success", data.message);
                } else
                {
                    showMessage("error", data.message);
                }
            })
            .catch((error) =>
            {
                showMessage("error", "An error occurred: " + error.message);
            });
    });

    // capture CTRL + S and click saveButton
    document.addEventListener("keydown", e =>
    {
        if (e.ctrlKey && e.key == "s")
        {
            // Prevent save dialog from opening
            e.preventDefault();

            saveButton.click();
            // trigger click animation
            saveButton.classList.add("active");
            setTimeout(() => saveButton.classList.remove("active"), 100);
        }
    });
});


