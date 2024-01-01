
let flag1,flag2,flag3=true;
function validate() {

     
     
     let Username=document.getElementById("floatingInput1").value;
     let pw=document.getElementById("floatingPassword1").value;
     let rpw=document.getElementById("floatingPassword2").value;
     let email=document.getElementById("floatingInput2").value;
     let divEmail=document.getElementById("email");
     let divUserName=document.getElementById("Username");
     let divpw=document.getElementById("pw");
     let divrpw=document.getElementById("rpw");
     

     const regex = /[ `!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
     console.log(typeof(pw),rpw,Username,email)
     
     if(Username===""){
          console.log("Username error")
          divUserName.innerHTML=`<input type="text" class="form-control is-invalid" id="floatingInput1" placeholder="Username@example.com">
          <label for="floatingInputInvalid">UserName is required</label>`;
          flag2=false;
     }
     else{
          divUserName.innerHTML=`<input type="email" class="form-control" id="floatingInput1" placeholder="Username@example.com" value=${Username}>
          <label for="floatingInput">UserName</label>`;
          flag2=true;
     }
     if(!email.includes("@")){
          
          divEmail.innerHTML=`<input type="email" class="form-control is-invalid" id="floatingInput2" placeholder="Username@example.com">
          <label for="floatingInputInvalid">Invalid Email</label>`;
          flag1=false;
     }
     else{
          divEmail.innerHTML=`<input type="email" class="form-control" id="floatingInput2" placeholder="Username@example.com" value=${email} >
          <label for="floatingInput">Email address</label>`;
          flag1=true;
     }
     if(pw.length<8){
          
          divpw.innerHTML=`<input type="password" class="form-control is-invalid" id="floatingPassword1" placeholder="Username@example.com" value=${pw}>
          <label for="floatingInputInvalid">No. of charecters must be 8 or more</label>`;
          flag3=false;
     }

     else if(pw===pw.toUpperCase() || pw===pw.toLowerCase()){
          
          divpw.innerHTML=(`<input type="password" class="form-control is-invalid" id="floatingPassword1" placeholder="Username@example.com" value=${pw}>
          <label for="floatingInputInvalid">must contain both uppercase and lowercase letters</label>`);
          flag3=false;
     }
     else if(pw.includes(Username) || pw.toLowerCase().includes(Username.toLowerCase())|| pw.toUpperCase().includes(Username.toUpperCase())){
          
          divpw.innerHTML=(`<input type="password" class="form-control is-invalid" id="floatingPassword1" placeholder="Username@example.com" value=${pw}>
          <label for="floatingInputInvalid">password must not include your Username</label>`);
          flag3=false;
     }
     else if(!regex.test(pw)){
          
          divpw.innerHTML=`<input type="password" class="form-control is-invalid" id="floatingPassword1" placeholder="Username@example.com" value=${pw}>
          <label for="floatingInputInvalid">password must contain a special character</label>`;
          flag3=false;
     }
     else if(!(pw===rpw)){
          
          divrpw.innerHTML=(`<input type="password" class="form-control is-invalid" id="floatingPassword2" placeholder="Username@example.com" value=${rpw}>
          <label for="floatingInputInvalid">repeat password is not same as password</label>`);
          flag3=false;
     }
     else{
          divpw.innerHTML=`<input type="password" class="form-control" id="floatingPassword1" placeholder="Password" value=${pw}>
          <label for="floatingPassword">Password</label>`;
          divrpw.innerHTML=`<input type="password" class="form-control" id="floatingPassword2" placeholder="Password" value=${rpw} >
          <label for="floatingPassword">Repeat Password</label>`;
          flag3=true;
     }
          
     
     
}


