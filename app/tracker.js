//this file is used to track visits to a page. It will send a request to the backend with the user agent, target url, and referrer.

async function trackVisit(user_agent, target_url, referrer) {
    const data = {
        user_agent: user_agent,
        target_url: target_url,
        referrer: referrer
    }

    try{
        const response = await fetch("{{API_URL}}/track", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Visit tracked successfully:", result);
    }catch(error){
        console.error("Error tracking visit:", error);
    }

}

//call the trackVisit one time when the page is loaded
window.addEventListener("load", () => {
    const user_agent = navigator.userAgent;
    const target_url = window.location.href;
    const referrer = document.referrer;

    trackVisit(user_agent, target_url, referrer);
});
