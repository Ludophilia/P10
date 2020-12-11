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

// Pour déclencher la fenetre qui suggère des requêtes de recherche
function displaySuggestions (search_suggestions_js, extra_par) {

    const query = extra_par.query
    const parent_form = extra_par.parent_form

    const search_suggestions = JSON.parse(search_suggestions_js)

    // Ajouter ou rafrachir la fenetre

    if (parent_form.querySelectorAll(".autocomplete-items").length >= 1) {
        parent_form.removeChild(parent_form.querySelector(".autocomplete-items"))
    }
    parent_form.insertAdjacentHTML("beforeend", "<div class='autocomplete-items'></div>")
    
    // AJouter les suggestions à la fenetre.

    search_suggestions.suggestions.forEach(
        (suggestion) => {
            const suggested = suggestion.slice(query.length) // Ou slice(0, query.length) si on veut mettre en valeur ce qu'à tapé l'utilisateur ou slice(query.length) si on veut mettre les suggestions en valeur
            const search_input = parent_form.querySelector("input")

            suggestion = suggestion.replace(suggested, `<b>${suggested}</b>`)
            parent_form.querySelector(".autocomplete-items").insertAdjacentHTML("beforeend",
            `<div class="ac-item"> ${suggestion} </div>`)

            parent_form.querySelector(".ac-item:last-child").addEventListener("click", (event) => {
                // On récupère la valeur
                if (event.target.classList.length === 0) {
                    search_input.value = event.target.parentNode.textContent.trim()
                } else {
                    search_input.value = event.target.textContent.trim()
                }
                // simuler appui sur la touche entrée
                parent_form.querySelector("button").click()
            })
        })
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

    // Observateurs de l'autocomplete des requetes
    document.querySelectorAll("input[type=search]").forEach(
        (search_input) => {
            // Un observateur d'évènements, qui après un input clavier, envoie une requête à la viewfunction, si la recherche est fructueuse, une fenetre s'affiche avec les suggestions
            search_input.addEventListener("keyup", (e) => {
            
                // Envoyer la requête au serveur
                const query = encodeURIComponent(e.target.value.trim()) // Pas un meilleur moyen ? Encode url
                const parent_form = e.target.parentNode
    
                if (query.length > 0) {
                    ajaxCommunicate("GET", `/suggest?query=${query}`, displaySuggestions, null, {"query": query, "parent_form": parent_form})
                } else {
                    if (parent_form.querySelectorAll(".autocomplete-items").length > 0) {
                        parent_form.querySelector(".autocomplete-items").classList.add("d-none")
                    } // Cache la fenêtre si la recherche est vide, elle sera supprimée et reconstruite à la prochaine requête
                }
            })
    
            // Retrouver la fenetre quand on remet le focus sur l'input
            search_input.addEventListener("focus", (e) => {
                
                const parent_form = e.target.parentNode
                
                if (e.target.value !== "") {
                    if (parent_form.querySelector(".autocomplete-items").classList.contains("d-none")) {
                        parent_form.querySelector(".autocomplete-items").classList.remove("d-none")
                    }
                }
            })
    
            // Masquer la fenetre quand on perd le focus...
            search_input.addEventListener("blur", (e) => {
                
                const parent_form = e.target.parentNode
    
                if (e.target.value !== "") {
                    if (parent_form.querySelectorAll(".autocomplete-items").length > 0) {
    
                        setTimeout(() => {
                            parent_form.querySelector(".autocomplete-items").classList.add("d-none")
                        }, 200) // Pour contrer le fait que Le blur se déclenche avant le clic sur la fenetre autocomplete.
                    }
                }
            })
        }
    )
}

main();