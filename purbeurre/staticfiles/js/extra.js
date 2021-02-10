// Pour récupérer le csrf_token
function getCookie(name) {

    var cookieValue = null;
    document.cookie.split(';').forEach(
        (cookie) => {
            cookie = cookie.trim();
            if(new RegExp(`^${name}`).test(cookie)) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            }
        }
    )
    return cookieValue
}

// Pour renvoyer les informations de produit au serveur 
function ajaxCommunicate(method, url, callback, data, extra_par) {

    const request = new XMLHttpRequest()
    request.open(method, url)
    
    if (method === "POST") {
        const csrftoken = getCookie('csrftoken');
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        request.setRequestHeader("X-CSRFToken", csrftoken);
    }

    request.addEventListener("load", function () { 
        if (request.status >= 200 && request.status < 400) { 
            if (extra_par !== "undefined") {
                callback(request.responseText, extra_par);
            } else {
                callback(request.responseText);
            }
        } else {
            console.error(request.status + " " + request.statusText); 
        }
    });
    request.addEventListener("error", function () { 
        console.error("Erreur réseau");
    });

    request.send(data); 
}	

// Pour déclencher l'envoi des infos de produit au serveur
function confirmToUser(responseText, event) {
    
    const correspondances = { 
        SaveOK: "Sauvegardé",
        UnsaveOK: "Sauvegarder",
        SaveError: "Erreur"
    }

    event.target.innerText = correspondances[responseText]
}

// Main function
function main() {

    // Observateurs qui gèrent la sauvegarde aliment
    document.querySelectorAll(".save-link").forEach(
        (link) => {
            link.addEventListener("click", (event) => {
    
                event.preventDefault()
                
                const substitute_name = event.target.dataset.url
                const isSaveRequest = event.target.innerText === "Sauvegarder" ? true : false 
        
                ajaxCommunicate(
                    "POST",
                    "/save", 
                    confirmToUser,
                    `request=${isSaveRequest? "" : "un"}save&substitute=${substitute_name}`,
                    event)
            })
        }
    )
}

main();