var uploader = document.getElementById('uploader');
var chooseButton = document.getElementById('chooseButton');
var fileButton = document.getElementById('fileButton')
chooseButton.addEventListener('change', function(e){
  console.log("In change");
  file = e.target.files[0];
})
// fileButton.addEventListener('click', function(e){
//   console.log("In upload");
//   var storageRef = firebase.storage().ref('Zip/'+file.name);
//   var task = storageRef.put(file);
//   task.on('state_changed', function progress(snapshot) {
//   var percentage = (snapshot.bytesTransferred/snapshot.totalBytes)*100;
//   uploader.value = percentage;
// }, function error(err) {

// },function complete() {

// });
// });