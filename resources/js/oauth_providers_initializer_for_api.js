var state_code,
    next_location = new URLSearchParams(window.location.search).get('next');

function storeStateCode(code) {
    state_code = code
}

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
            $.ajax({
                url: "/login?from=login_dialog",
                async: false,
                success: storeStateCode
            });
            auth2.grantOfflineAccess().then((authResult)=>{
                $.ajax({
                    'type': 'POST',
                    'url': `/login?state=${state_code}&for=api`,
                    'processData': false,
                    'contentType': 'application/octet-stream; charset=utf-8',
                    'data': authResult['code'],
                    'success': (result) => {
                        document.write("<pre>" + result + "</pre>")
                        setTimeout(()=>{
                            window.location.href = next_location ? next_location : '/api/v1/get_access_token';
                        }, 2000);
                    }
                })
            })
        });
    }

function getLoginState() {
    init();
}