
window.onload = function() {
  serverText = document.querySelector('.server');
  serverText.innerHTML = "Server: " + (CURRENTWEB == LOCALWEB ? "Local" : "Camp");
}

const submitbtn = document.querySelector('.submitbtn');
const search = document.querySelector('.inputsearch');
const searchresult = document.querySelector('.resultfound');
let searchresulthref = null;
const searchresults = document.querySelector('.searchresults');

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
        let searchnum = 0;
        searchresults.innerHTML = "";
        console.log(data)
        console.log(data.length);
        if (data.length < 2 || data.length === undefined){
            createErrorMsg("No results found.");
            loadingToggle("off");
            searchresult.style.display = "flex";
            searchresult.innerHTML = "Found " + searchnum/2 + " results.";
            searchresulthref = document.querySelector('.searchresulthref');
            return;
        }
        data.forEach(element => {
            if (element.length !== 0){
                console.log(searchnum+1);
                let newDiv = document.createElement('div');
                newDiv.classList.add('searchresult');
                newDiv.innerHTML = `
                    <a class="searchresulthref" href="communityview.html?=${element[searchnum]["$oid"]}">
                    <p class="searchresultdesc">${element[searchnum+1]}</p>
                    <p class="searchresultid">${element[searchnum]["$oid"]}</p>
                `;
                document.querySelector('.searchresults').appendChild(newDiv);
                searchnum += 2;
            }
        });
        searchresult.style.display = "flex";
        searchresult.innerHTML = "Found " + searchnum/2 + " results.";
        searchresulthref = document.querySelector('.searchresulthref');
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

if (searchresulthref)
{
        searchresulthref.addEventListener("click", (event) => {
        let target = event.target;
        let id = target.closest(searchresulthref).querySelector('.searchresultid').innerHTML;
        console.log(id);
        localStorage.setItem("communityid", id);
    })
}
