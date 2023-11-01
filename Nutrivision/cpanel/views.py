from django.shortcuts import render, redirect
from django.contrib import auth
import pyrebase
from django.contrib.auth import logout


config = {
    "apiKey": "AIzaSyDoYIMA5UKw6nPpoMiAI7ggtYZ5O37Mrsk",
    "authDomain": "nutri-vision.firebaseapp.com",
    "databaseURL": "https://nutri-vision-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "nutri-vision",
    "storageBucket": "nutri-vision.appspot.com",
    "messagingSenderId": "852048295193",
    "appId": "1:852048295193:web:440941bd658a175b3b4188",
    "measurementId": "G-5QTY9FF24S",
}

firebase = pyrebase.initialize_app(config)

database = firebase.database()
auth = firebase.auth()


def signIn(request):
    return render(request, "signIn.html")


def postSignIn(request):
    email = request.POST.get("email")
    passw = request.POST.get("pass")

    try:
        user = auth.sign_in_with_email_and_password(email, passw)
    except Exception as e:
        message = "Invalid credentials: " + str(e)
        return render(request, "signIn.html", {"messg": message})

    idtoken = user["idToken"]

    # Get the user's email verification status
    user_info = auth.get_account_info(idtoken)
    email_verified = user_info["users"][0]["emailVerified"]

    if not email_verified:
        message = "Email not verified. Please check your inbox and verify your email."
        return render(request, "signIn.html", {"messg": message})

    a = user_info["users"][0]["localId"]

    name = database.child("users").child(a).child("details").child("name").get().val()
    return render(request, "welcome.html", {"email": name})


def logout(request):
    auth.current_user = None
    return render(request, "signIn.html")

    


def signUp(request):
    return render(request, "signUp.html")


# def postSignUp(request):
#     name = request.POST.get("name")
#     email = request.POST.get("email")
#     passw = request.POST.get("pass")
#     try:
#         user = auth.create_user_with_email_and_password(email, passw)
#         auth.send_email_verification(user['idToken'])
#     except:
#         message = "unable to create account try again"
#         return render(request, "signUp.html", {"messg": message})

#     uid = user["localId"]

#     data = {"name": name, "status": "1"}
#     mssg = "you may now sign in"
#     database.child("users").child(uid).child("details").set(data)
#     return render(request, "signIn.html", {"messg": mssg})


def postSignUp(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    passw = request.POST.get("pass")
    try:
        user = auth.create_user_with_email_and_password(email, passw)

        # Send email verification
        auth.send_email_verification(user["idToken"])

    except Exception as e:
        message = "Unable to create account. Try again: " + str(e)
        return render(request, "signUp.html", {"messg": message})

    uid = user["localId"]

    data = {"name": name, "status": "1"}
    mssg = "A verification email has been sent to your email address. Please check your inbox and verify your email before signing in."
    database.child("users").child(uid).child("details").set(data)
    return render(request, "signIn.html", {"messg": mssg})


def create(request):
    return render(request, "create.html")


def post_create(request):
    import time
    import datetime
    from datetime import datetime, timezone
    import pytz

    tz = pytz.timezone("Asia/Kolkata")
    time_now = datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))

    work = request.POST.get("work")
    progress = request.POST.get("progress")
    url = request.POST.get("url")

    idtoken = request.session["uid"]
    a = auth.get_account_info(idtoken)
    a = a["users"]
    a = a[0]
    a = a["localId"]

    data = {"work": work, "progress": progress, "url": url}

    database.child("users").child(a).child("reports").child(millis).set(data)
    name = database.child("users").child(a).child("details").child("name").get().val()

    return render(request, "welcome.html", {"email": name})


def check(request):
    import time
    import datetime
    from datetime import timezone

    idtoken = request.session["uid"]
    a = auth.get_account_info(idtoken)
    a = a["users"]
    a = a[0]
    a = a["localId"]
    timeStamps = database.child("users").child(a).child("reports").shallow().get().val()
    lis_time = []

    for time in timeStamps:
        lis_time.append(time)

    lis_time.sort(reverse=True)

    work = []

    for time in lis_time:
        work.append(
            database.child("users")
            .child(a)
            .child("reports")
            .child(time)
            .child("work")
            .get()
            .val()
        )

    date = []
    for i in lis_time:
        i = float(i)
        dat = datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")
        date.append(dat)

    comb_lis = zip(lis_time, date, work)

    name = database.child("users").child(a).child("details").child("name").get().val()
    return render(request, "check.html", {"comb_lis": comb_lis, "email": name})


def post_check(request):
    import datetime

    time = request.GET.get("z")
    idtoken = request.session["uid"]
    a = auth.get_account_info(idtoken)
    a = a["users"]
    a = a[0]
    a = a["localId"]

    work = (
        database.child("users")
        .child(a)
        .child("reports")
        .child(time)
        .child("work")
        .get()
        .val()
    )
    progress = (
        database.child("users")
        .child(a)
        .child("reports")
        .child(time)
        .child("progress")
        .get()
        .val()
    )
    img_url = (
        database.child("users")
        .child(a)
        .child("reports")
        .child(time)
        .child("url")
        .get()
        .val()
    )

    i = float(time)
    dat = datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")

    name = database.child("users").child(a).child("details").child("name").get().val()
    return render(
        request,
        "post_check.html",
        {"w": work, "p": progress, "d": dat, "email": name, "i": img_url},
    )
