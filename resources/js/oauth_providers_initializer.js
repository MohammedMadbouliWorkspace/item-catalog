var state_code,
    next_location = new URLSearchParams(window.location.search).get('next');

function init() {
        gapi.load('auth2', function () {
            auth2 = gapi.auth2.init({
                'client_id': '439760467294-5p30ja7ta1fngf9vu9pcahoq2imdvl5m.apps.googleusercontent.com',
                'cookie_policy': 'single_host_origin',
                'redirect_uri': 'postmessage',
                'fetch_basic_profile': 'false',
                'scope': 'openid',
                'prompt': 'consent'
            })
        });
        gapi.signin2.render('signInButton', {
            'width': 200,
            'height': 40,
            'longtitle': true
        });
        $('#signInButton').click(()=>{
            auth2.grantOfflineAccess().then((authResult)=>{
                $.ajax({
                    'type': 'POST',
                    'url': `/login?state=${state_code}`,
                    'processData': false,
                    'contentType': 'application/octet-stream; charset=utf-8',
                    'data': authResult['code'],
                    'success': () => {
                        window.location.href = next_location ? next_location : '';
                    }
                })
            })
        });
    }

function loginDialog() {
    var loginDialogOverlay = document.createElement("div");
    loginDialogOverlay.className = "overlay";
    loginDialogOverlay.innerHTML = `<div class="dialog"> <div class="content_block content_block_dark"> <h2> <span>Log in with:</span> <div class="update_links"> <a class="a_ul" id="cancel">Cancel</a> </div></h2> <div><div id="signInButton"></div></div></div></div>`;
    loginDialogOverlay.addEventListener("click", (e)=>{
        if(e.target.className == "overlay" || e.target.id == "cancel"){loginDialogOverlay.style.animationName="overlay-disappear";setTimeout(()=>{loginDialogOverlay.remove()},250)}
    });
    document.body.insertAdjacentElement("beforeend", loginDialogOverlay)
}

function storeStateCode(code) {
    state_code = code
}

function getLoginState() {
    $.ajax({
        url: "/login?from=login_dialog",
        async: false,
        success: storeStateCode
    });
    init();
}

let toggleLoginDialog = document.getElementById("toggleLoginDialog");
toggleLoginDialog.addEventListener("click", ()=>{
    loginDialog();
    getLoginState();
});