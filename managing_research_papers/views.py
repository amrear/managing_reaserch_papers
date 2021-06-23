from datetime import datetime
import time
import os
import re

from flask import render_template, redirect, url_for, session, request, flash, abort, send_from_directory
import bcrypt

from managing_research_papers import app, db
from managing_research_papers.forms import EnglishSubmit, FarsiSubmit, AdminSubmit
from managing_research_papers.models import Posts, PendingPosts


@app.route("/")
def index():
    """The index page."""

    # Website language is stored in a client side session.
    # Fetch that or use English by default if it doesn't exits.
    # This is a common pattern throughout the program.
    language = session.get("language", "English")

    # Fetch all of the posts from the database in descending order.
    posts = Posts.query.order_by(Posts.id.desc())

    # Render the the English or the Farsi version of the website based on the `language` variable.
    # This is a common pattern throughout the program.
    if language == "English":
        return render_template("en/index.html", title="Home", posts=posts)
    elif language == "Farsi":
        return render_template("fa/index.html", title="خانه", posts=posts)


@app.route("/en")
def en():
    """Set the language session to English."""
    session["language"] = "English"
    return redirect(request.referrer)


@app.route("/fa")
def fa():
    """Set the language session to Farsi."""
    session["language"] = "Farsi"
    return redirect(request.referrer)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    """Submit a new post to the `PendingPosts` for the admins to verify and to be added to the site."""

    # Read the `language` session or use English be default if there is no session.
    language = session.get("language", "English")

    # Create the right form object based on the website language to be rendered.
    if language == "English":
        form = EnglishSubmit()
    elif language == "Farsi":
        form = FarsiSubmit()

    # Check if all of the inputs were properly filled.
    # If true, store all of them and save the files in the filesystem.
    # Then redirect the user to the homepage.
    # Use the current time in nanoseconds for the filename to avoid naming collisions and files overwriting eachother.
    if form.validate_on_submit():
        post = PendingPosts(
            title=form.title.data,
            language=language,
            publish_date=datetime(
                form.publish_date.data.year, form.publish_date.data.month, form.publish_date.data.day),
            journal_type=form.journal_type.data,
            scientific_degree=form.scientific_degree.data,
            impact_factor=form.impact_factor.data,
            abstracting_and_indexing=form.abstracting_and_indexing.data,
            doi=form.doi.data,
            indexing_certificate_filename=f"{time.time_ns()}{os.path.splitext(form.indexing_certificate_file.data.filename)[1]}",
            author_count=form.authors_count.data,
            poster_authorship=form.poster_authorship.data,
            poster_academic_rank=form.poster_academic_rank.data,
            poster_name=form.poster_name.data,
            poster_lastname=form.poster_lastname.data,
            poster_email=form.poster_email.data,
            poster_affiliation=form.poster_affiliation.data,
            abstract=form.abstract.data,
            keywords=form.keywords.data,
            scientific_field=form.scientific_field.data,
            journal_filename=f"{time.time_ns()}.pdf"
        )

        # Add the new post to the database.
        db.session.add(post)
        db.session.commit()

        # Save the files in the filesystem with the same filename stored in the database.
        form.journal_file.data.save(
            os.path.join("managing_research_papers/uploads/journals", post.journal_filename))

        form.indexing_certificate_file.data.save(
            os.path.join("managing_research_papers/uploads/indexing_certificate_files", post.indexing_certificate_filename))

        # If everything went okay, redirect the user to the homepage with a message to inform them that the post
        # has been submitted and will be added to the website in their preferred language.
        if language == "English":
            flash(
                "Your post has been submitted and will be added to the website after our admins' approval.", "success")

        elif language == "Farsi":
            flash("پست شما ثبت شد و پس از تایید مدیران در سایت قرار می‌گیرد.", "success")

        return redirect(url_for("index"))

    # If the request method is GET, simply render the submit pages.
    if language == "English":
        return render_template("en/submit.html", title="Submit New Posts", form=form)
    elif language == "Farsi":
        return render_template("fa/submit.html", title="مقاله خود را منتشر کنید", form=form)


@app.route("/post/<int:id>")
def post(id):
    """Fetch an individual post with a specific `id` and show it to user."""

    # Create the right form object based on the website language to be rendered.
    language = session.get("language", "English")

    # Try to fetch the post from the database.
    post = Posts.query.get(id)

    # If the post doesn't exist, give an HTTP status code of 404.
    if post is None:
        abort(404)

    # Split the abstract to a list of paragraphs based on the newlines,
    # to seprate them properly in the html template, and format them nicely for the user.
    abstract = [paragraph.strip()
                for paragraph in post.abstract.split("\n") if paragraph]

    # Split the keywords into a list with a comma delimiter.
    # Since there are different comma characters in English and Farsi, we have to take care of that as well.
    keywords = [keyword.strip()
                for keyword in re.split(",|،", post.keywords) if keyword]

    # Render the post in user's preferred language.
    if language == "English":
        return render_template("en/post.html", title=post.title, post=post, abstract=abstract, keywords=keywords)
    elif language == "Farsi":
        return render_template("fa/post.html", title=post.title, post=post, abstract=abstract, keywords=keywords)


@app.route("/search")
def search():
    """Search the posts for with a specific query and render the results."""

    # Create the right form object based on the website language to be rendered.
    language = session.get("language", "English")

    # This is the HTTP GET parameter for the search keyword.
    q = request.args.get("q")

    # If an HTTP parameter is given, search the database with the value of that parameter.
    # Currently it searches it the title, abstract, and the keywords of the post, but that can be changed easily.
    if q:
        posts = Posts.query.filter(Posts.title.contains(
            q) | Posts.abstract.contains(q) | Posts.keywords.contains(q))

        # Render the post in user's preferred language.
        if language == "English":
            return render_template("en/index.html", title=q, q=q, posts=posts)
        elif language == "Farsi":
            return render_template("fa/index.html", title=q, q=q, posts=posts)

    # If the user haven't specified any keyword in their search, redirect them to the homepage.
    return redirect(url_for("index"))


@app.route("/download/<int:id>")
def download(id):
    """Download the journal file with a specific id."""

    # Try query the required post by `id` from the database.
    post = Posts.query.get(id)

    # Give a 404 HTTP status code if the post with the specified id doesn't exist.
    if post is None:
        abort(404)

    # Send the file to the user to download.
    return send_from_directory("uploads/journals/", post.journal_filename)


@app.route("/indexing_certificate_download/<int:id>")
def indexing_certificate_download(id):
    """Download the indexing certificate file of a post with a specific id."""

    # Try query the required post by `id` from the database.
    post = Posts.query.get(id)

    # Give a 404 HTTP status code if the post with the specified id doesn't exist.
    if post is None:
        abort(404)

    # Send the file to the user to download.
    return send_from_directory("uploads/indexing_certificate_files", post.indexing_certificate_filename)


# The following are the admin routes of the application.
# A lot of the features are similar to the non-admin section.
# I didn't comment the similar functionality anymore.
# Some of the functions are equivalent to the non admin ones except that they can
# access the pending data as well.


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """The login page for the admin section."""

    # If the admin session is set to True, redirect the user to the admin homepage.
    if session.get("admin"):
        return redirect(url_for("admin_index", status="current"))

    # If the request method is POST and the username and password are correct, redirect the user to the admin homepage.
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # If the fields were empty redirect user back to the login page with the proper error message.
        if not username or not password:
            return render_template("/admin/login.html", title="Login", errors=["Some of the fields are empty."])

        # If username and password are correct, send the user to the admin homepage.
        # The password is hashed using the `bcrypt.hashpw` function.
        if username == "username" and bcrypt.checkpw(
                password.encode(), b'$2b$12$QVK.5IESlPqYJRSEQRdQC.AwoVRiDJdpM9hBIf.6aIpAT090zFXCW'):
            session["admin"] = True
            return redirect(url_for("admin"))

        # If both of the fields are filled but the provided information is erroneous, redirect the user back to the login page.
        return render_template("/admin/login.html", title="Login", errors=["The username or the password are not correct."])

    # If the admin session is not set and the request method is GET, just render the login page.
    return render_template("admin/login.html", title="Login", errors=[])


@app.route("/admin/<string:status>")
def admin_index(status):
    """The index page for admin."""

    # If admin session is not set to True, redirect the user to the login page.
    # This is a common pattern in the admin routes to make sure ordinary users don't have access to the admin sections.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # `status` can have two values, current and pending.
    # current means the posts that are already verified by the admin and can be shown to the users of the site.
    # pending means the posts that are not verified yet.
    # Anything other than that is an invalid route.
    # The application shows the suitable posts based on the value of status.
    # This is a common pattern throughout the application.
    if status == "current":
        posts = Posts.query.order_by(Posts.id.desc())
    elif status == "pending":
        posts = PendingPosts.query.order_by(PendingPosts.id.desc())
    else:
        abort(404)

    return render_template("admin/index.html", title=f"Admin - {status.title()}", posts=posts, status=status)


@app.route("/admin/<string:status>/post/<int:id>")
def admin_post(status, id):
    """Queries the database for a pending of current post based on a specific id."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Check for the status to load the appropriate content.
    if status == "current":
        post = Posts.query.get(id)
        if post is None:
            abort(404)
    elif status == "pending":
        post = PendingPosts.query.get(id)
        if post is None:
            abort(404)
    else:
        abort(404)

    # Split the abstract to a list of paragraphs based on the newlines,
    # to seprate them properly in the html template, and format them nicely for the user.
    abstract = [paragraph.strip()
                for paragraph in post.abstract.split("\n") if paragraph]

    # Split the keywords into a list with a comma delimiter.
    # Since there are different comma characters in English and Farsi, we have to take care of that as well.
    keywords = [keyword.strip()
                for keyword in re.split(",|،", post.keywords) if keyword]

    return render_template("admin/post.html", title=post.title, post=post, abstract=abstract, keywords=keywords, status=status)


@app.route("/admin/search")
def admin_search():
    """Search the current and pending posts for with a specific query and render the results."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # This is the HTTP GET parameter for the search keyword.
    q = request.args.get("q")

    # If an HTTP parameter is given, search the database with the value of that parameter.
    # Currently it searches it the title, abstract, and the keywords of the post, but that can be changed easily.
    # In contrast to the `search` function, this function searches both `Posts` and `PendingPosts` tables
    # and labels the pending posts when rendering the page.
    if q:
        posts = Posts.query.filter(Posts.title.contains(
            q) | Posts.abstract.contains(q) | Posts.keywords.contains(q))

        pending_posts = PendingPosts.query.filter(PendingPosts.title.contains(
            q) | PendingPosts.abstract.contains(q) | PendingPosts.keywords.contains(q))

        return render_template("admin/search.html", title=q, q=q, posts=posts, pending_posts=pending_posts)

    # If no keyword is given to search, redirect to the admin homepage.
    return redirect(url_for("admin_index", status="current"))


@app.route("/admin/<string:status>/download/<int:id>")
def admin_download(status, id):
    """Download the journal file of a pending or current post with a specific id."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Depending on the `status`, query the `Posts` or the `PendingPosts` tables.
    # This is in contrast to the regular `admin` function which is only capable of querying `Posts`.
    if status == "current":
        post = Posts.query.get(id)
        if post is None:
            abort(404)
    elif status == "pending":
        post = PendingPosts.query.get(id)
        if post is None:
            abort(404)
    else:
        abort(404)

    # Send the file to the user to download.
    return send_from_directory("uploads/journals", post.journal_filename)


@app.route("/admin/<string:status>/indexing_certificate_download/<int:id>")
def admin_indexing_certificate_download(status, id):
    """Download the indexing certificate file of a pending or current post with a specific id."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Depending on the `status`, query the `Posts` or the `PendingPosts` tables.
    # This is in contrast to the regular `admin_indexing_certificate` function which is only capable of querying `Posts`.
    if status == "current":
        post = Posts.query.get(id)
        if post is None:
            abort(404)
    elif status == "pending":
        post = PendingPosts.query.get(id)
        if post is None:
            abort(404)
    else:
        abort(404)

    return send_from_directory("uploads/indexing_certificate_files/", post.indexing_certificate_filename)


@app.route("/admin/<string:status>/edit/<int:id>", methods=["GET", "POST"])
def admin_edit(status, id):
    """Edit an existing post (pending or currend depending on the status variable)."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Depending on the status, query for the post with a specific `id`,
    # if the post doesn't exist, return an HTTP 404 status code.
    if status == "current":
        post = Posts.query.get(id)
        if post is None:
            abort(404)
    elif status == "pending":
        post = PendingPosts.query.get(id)
        if post is None:
            abort(404)
    else:
        abort(404)

    form = AdminSubmit()

    # If the HTTP method is POST and all of the inputs have valid values,
    # overwrite the given values on the previous ones except for the filenames.
    if form.validate_on_submit():
        post.title = form.title.data
        post.publish_date = datetime(
            form.publish_date.data.year, form.publish_date.data.month, form.publish_date.data.day)
        post.journal_type = form.journal_type.data
        post.language = form.language.data.title()
        post.scientific_degree = form.scientific_degree.data
        post.impact_factor = form.impact_factor.data
        post.abstracting_and_indexing = form.abstracting_and_indexing.data
        post.doi = form.doi.data
        post.author_count = form.authors_count.data
        post.poster_authorship = form.poster_authorship.data
        post.poster_academic_rank = form.poster_academic_rank.data
        post.poster_name = form.poster_name.data
        post.poster_lastname = form.poster_lastname.data
        post.poster_email = form.poster_email.data
        post.poster_affiliation = form.poster_affiliation.data
        post.abstract = form.abstract.data
        post.keywords = form.keywords.data
        post.scientific_field = form.scientific_field.data

        # If the indexing certificate field wasn't empty, remove the previous indexing certificate file and save the new one.
        if form.indexing_certificate_file.data:
            # Remove the previous file.
            os.remove(
                os.path.join("managing_research_papers/uploads/indexing_certificate_files", post.indexing_certificate_filename))

            # Store the current number of nanoseconds in the database as the filename.
            filename = f"{time.time_ns()}{os.path.splitext(form.indexing_certificate_file.data.filename)[1]}"
            post.indexing_certificate_filename = filename

            # Save the new file into the filesystem.
            form.indexing_certificate_file.data.save(
                os.path.join("managing_research_papers/uploads/indexing_certificate_files", filename))

        # Likewise do the same for the journal file field
        if form.journal_file.data:
            # Remove the previous file.
            os.remove(
                os.path.join("managing_research_papers/uploads/journals", post.journal_filename))

            # Store the current number of nanoseconds in the database as the filename.
            filename = f"{time.time_ns()}.pdf"
            post.journal_filename = filename

            # Save the new file into the filesystem.
            form.journal_file.data.save(
                os.path.join("managing_research_papers/uploads/journals", filename))

        # Save the changes to the database.
        db.session.commit()

        # Redirect the user to the post page with a message to inform them that the edit was successful.
        flash("The post has been edited.", "success")
        return redirect(url_for("admin_post", status=status, id=id))

    return render_template("admin/edit.html", title=f"Edit - {post.title}", form=form, post=post)


@app.route("/admin/submit", methods=["GET", "POST"])
def admin_submit():
    """Submit a new post directly to the `Posts` table."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    form = AdminSubmit()

    # If the form is filled properly, submit the information to the database and save the files to the filesystem.
    if form.validate_on_submit():
        post = Posts(
            title=form.title.data,
            language=form.language.data.title(),
            publish_date=datetime(
                form.publish_date.data.year, form.publish_date.data.month, form.publish_date.data.day),
            journal_type=form.journal_type.data,
            scientific_degree=form.scientific_degree.data,
            impact_factor=form.impact_factor.data,
            abstracting_and_indexing=form.abstracting_and_indexing.data,
            doi=form.doi.data,
            indexing_certificate_filename=f"{time.time_ns()}{os.path.splitext(form.indexing_certificate_file.data.filename)[1]}",
            author_count=form.authors_count.data,
            poster_authorship=form.poster_authorship.data,
            poster_academic_rank=form.poster_academic_rank.data,
            poster_name=form.poster_name.data,
            poster_lastname=form.poster_lastname.data,
            poster_email=form.poster_email.data,
            poster_affiliation=form.poster_affiliation.data,
            abstract=form.abstract.data,
            keywords=form.keywords.data,
            scientific_field=form.scientific_field.data,
            journal_filename=f"{time.time_ns()}.pdf"
        )

        # Submit the data to the database.
        db.session.add(post)
        db.session.commit()

        # Save the files to the filesystem.
        form.journal_file.data.save(
            os.path.join("managing_research_papers/uploads/journals", post.journal_filename))

        form.indexing_certificate_file.data.save(
            os.path.join("managing_research_papers/uploads/indexing_certificate_files", post.indexing_certificate_filename))

        # Redirect the user to the homepage wih a message to inform them that the submission was successful.
        flash("The post has been added to the website.", "success")

        return redirect(url_for("admin_index", status="current"))

    return render_template("admin/submit.html", title="Admin - Submit", form=form)


@app.route("/admin/add_pending/<int:id>")
def admin_add_pending(id):
    """Add an entry with a specific `id` from the `PendingPosts` table to the `Posts` table in the database."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Query the post from the `PendigPosts`
    pending_post = PendingPosts.query.get(id)

    post = Posts(
        title=pending_post.title,
        language=pending_post.language,
        publish_date=pending_post.publish_date,
        journal_type=pending_post.journal_type,
        scientific_degree=pending_post.scientific_degree,
        impact_factor=pending_post.impact_factor,
        abstracting_and_indexing=pending_post.abstracting_and_indexing,
        doi=pending_post.doi,
        indexing_certificate_filename=pending_post.indexing_certificate_filename,
        author_count=pending_post.author_count,
        poster_authorship=pending_post.poster_authorship,
        poster_academic_rank=pending_post.poster_academic_rank,
        poster_name=pending_post.poster_name,
        poster_lastname=pending_post.poster_lastname,
        poster_email=pending_post.poster_email,
        poster_affiliation=pending_post.poster_affiliation,
        abstract=pending_post.abstract,
        keywords=pending_post.keywords,
        scientific_field=pending_post.scientific_field,
        journal_filename=pending_post.journal_filename
    )

    # Add the post to the `Posts` table and remove it from the `PendingPosts`.
    db.session.add(post)
    db.session.delete(pending_post)
    db.session.commit()

    # Redirect the user to the index homepage with a success message.
    flash("The post has been added to the website.", "success")
    return redirect(url_for("admin_index", status="current"))


@app.route("/admin/<string:status>/delete/<int:id>")
def admin_delete(status, id):
    """Delete a pending or a current post with a specific id from the database."""

    # If admin session is not set to True, redirect the user to the login page.
    if not session.get("admin"):
        return redirect(url_for("admin"))

    # Query for the post in the appropriate table.
    if status == "current":
        post = Posts.query.get(id)
        if post is None:
            abort(404)
    elif status == "pending":
        post = PendingPosts.query.get(id)
        if post is None:
            abort(404)
    else:
        abort(404)

    # First remove the files associated to the entry in the database from the filesystem.
    os.remove(
        os.path.join("managing_research_papers/uploads/journals", post.journal_filename))

    os.remove(
        os.path.join("managing_research_papers/uploads/indexing_certificate_files", post.indexing_certificate_filename))

    # Then delete the entry itself from the database and redirect the user to the admin homepage.
    db.session.delete(post)
    db.session.commit()

    flash("The post has been deleted.", "success")
    return redirect(url_for("admin_index", status=status))


@app.route("/admin/logout")
def admin_logout():
    """Set the admin session to False."""
    session["admin"] = False
    return redirect(url_for("index"))
