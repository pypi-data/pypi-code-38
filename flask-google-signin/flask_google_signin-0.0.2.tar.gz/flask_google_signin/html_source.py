login_page_html = '''
<head>
    <meta name="google-signin-client_id" content="{{client_id}}">
</head>

<body>
    <div id="my-signin2"></div>

    <script>

        function onSuccess(googleUser) {
            document.getElementById('display').innerHTML = 'Logging in! Redirecting...';
            var id_token = googleUser.getAuthResponse().id_token;
            gapi.auth2.getAuthInstance().signOut()
            gapi.auth2.getAuthInstance().disconnect()

            document.getElementById('id_token').value = id_token;
            document.getElementById("myForm").submit();
        }

        function onFailure(error) {
            document.getElementById('display').innerHTML = 'Login Fail! Try Again!';
        }

        function renderButton() {
            gapi.signin2.render('my-signin2', {
                'scope': 'profile email',
                'width': 240,
                'height': 50,
                'longtitle': true,
                'theme': 'dark',
                'onsuccess': onSuccess,
                'onfailure': onFailure
            });
        }

    </script>

    <script src="https://apis.google.com/js/platform.js?onload=renderButton" async defer></script>

    <p id="display"></p>

    <form id="myForm" action="{{url_for('google_signin.authorize')}}" method="post">
        <input id="id_token" type="hidden" name="id_token" value="">
        <input id="success_redirect" type="hidden" name="success_redirect" value="{{success_redirect}}">
    </form>
</body>
'''

login_success_html = '''
<head>
</head>

<body>
    <p>Login Success. Redirect now...</p>

    <script>
        window.setTimeout(function () {
            window.location.replace("{{success_redirect}}");
        }, 1000);

    </script>

</body>
'''
