
var searchArr;
// whether there is search history stored in browser
if(localStorage.search){
// if so, save to searchArr
    searchArr= localStorage.search.split(",")
}else{
// if not, searchArr will be an empty array
    searchArr = [];
}
// Search history will be what have been saved
MapSearchArr();


$("#btn").on("click", function(){
    var val = $("#inp").val();
// when click the search button -> remove duplicates
    KillRepeat(val);
// Restore searchArr to localStorage
    localStorage.search = searchArr;
// Show search content
    MapSearchArr();
});


function MapSearchArr(){
    var tmpHtml = "";
    for (var i=0;i<searchArr.length;i++){
        tmpHtml += "<span>" + searchArr[i] + "</span> "
    }
    $("#keyname").html(tmpHtml);
}
// remove duplicates
function KillRepeat(val){
    var kill = 0;
    for (var i=0;i<searchArr.length;i++){
        if(val===searchArr[i]){
            kill ++;
        }
    }
    if(kill<1){
        searchArr.push(val);
    }
}

