
window.onload = function() {
  serverText = document.querySelector('.server');
  serverText.innerHTML = "Server: " + (CURRENTWEB == LOCALWEB ? "Local" : "Camp");
}

const submitbtn = document.querySelector('.submitbtn');
const search = document.querySelector('.inputsearch');

function loadingToggle(str){
    if (str === "on"){
        document.querySelector('.loadinggif').style.display = "flex";
        submitbtn.style.cursor = "not-allowed";
        submitbtn.style.filter = "brightness(70%)";
    }
    else if (str === "off") {
        document.querySelector('.loadinggif').style.display = "none";
        submitbtn.style.cursor = "pointer";
        submitbtn.style.filter = "brightness(100%)";
    }
    return;
}

function createErrorMsg(str){
    document.querySelector('.footerdesc').style.display = "flex";
    document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
    document.querySelector('.footerdesc').innerHTML = str;
    setTimeout(() => {
      document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
    }, 2000);
    document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    return;
}

function processSearch() {
    const searchValue = search.value;

    if (searchValue === ""){
        createErrorMsg("Please enter a valid search query.");
        return;
    }

    loadingToggle("on");

    //searching for database
    fetch(CURRENTWEB + "communitySearch", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(searchValue)
    })
    .then((response) => response.json())
    .then((data) => { //data is an array of objects
        console.log(data)
        console.log(data.length);
        if (data.length === 0){
            createErrorMsg("No results found.");
            return;
        }
        document.querySelector('.searchresults').style.display = "flex";
        document.querySelector('.searchresults').innerHTML = "";
        data.forEach(element => {
            let newDiv = document.createElement('div');
            newDiv.classList.add('searchresult');
            newDiv.innerHTML = `
                <p class="resulttitle">${element.title}</p>
                <p class="resultdesc">${element.description}</p>
                <p class="resultlink"><a href="${element.link}" target="_blank">View</a></p>
            `;
            document.querySelector('.searchresults').appendChild(newDiv);
        });
        loadingToggle("off");
    })
    .catch((error) => {
        console.error("Error:", error);
        createErrorMsg(error);
        loadingToggle("off");
    });

    return;
}

search.addEventListener("keydown" , e => {
    if (e.key === "Enter"){
        processSearch();
    }
});

submitbtn.addEventListener("click", () => {
    processSearch();
})