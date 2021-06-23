from datetime import date

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileSize
from wtforms import StringField, RadioField, SelectField, TextAreaField, SubmitField, FileField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange
from wtforms.fields.html5 import DateField
from wtforms.widgets.html5 import NumberInput

# You can specify the filesize of the certificate and journal files here in bytes.
# Don't forget to change the error message in the classes afterwards for the maximum filesize.
INDEXING_CERTIFICATE_FILE_MAXSIZE = 2 * 1024 * 1024
ARTICLE_FILE_MAXSIZE = 16 * 1024 * 1024

# These 3 classes represent the Farsi and English submit forms and also the submit form in the admin secion respectively.

class FarsiFloatField(FloatField):
    # The reasons I'm subclassing the FloatField is to change it's error message to Farsi when 
    # the input is not right and the language of the website is Farsi.
    # Unfortunately the writers of this class have not provided an easier way to change its error message.

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext(
                    'مقدار ورودی یک عدد اعشاری معتبر نیست.'))


class EnglishSubmit(FlaskForm):
    """The submit form for the English version of the website."""
    # Every variable in this class is a field of our form.
    # Each field has a validator keyword argument, which is used to specifies how the field should be examined.
    # There is an optional message argument for some of the validators, which specifies what message should be shown
    # to the user in the case of an error, I have changed some of the messages since the default ones were opaque a bit.
    # Particularly the `FileField`s.
    # There is also a `validate_publish_date` method which checks to see if the inputted date is valid or not. 
    title = StringField("Title", validators=[DataRequired(), Length(max=64)])

    publish_date = DateField(
        "Publish date", format=r"%Y-%m-%d", validators=[DataRequired()])

    journal_type = RadioField("Journal type", choices=[
        "Magazine", "Conference"], validators=[DataRequired()])

    scientific_degree = SelectField("Scientific degree", choices=["ISI", "ISC", "Scientific research",
        "Scientific review", "None"], validators=[DataRequired()])

    impact_factor = FloatField("Impact factor")

    abstracting_and_indexing = SelectField("Abstracting and indexing", choices=["ISI (web of science)", "Scopus",
        "Pubmed"], validators=[DataRequired()])

    doi = StringField("DOI", validators=[DataRequired(), Length(max=128)])

    indexing_certificate_file = FileField("Indexing certificate file", validators=[FileRequired(),
        FileAllowed(["jpg", "jpeg", "png"]), FileSize(INDEXING_CERTIFICATE_FILE_MAXSIZE, 
        message="Filesize should be 2 Megabytes at maximum.")])

    authors_count = IntegerField("Number of authors", widget=NumberInput(
        ), validators=[DataRequired(), NumberRange(min=1, max=10)])

    poster_authorship = SelectField("Your authorship", choices=["Co-author", "First author", "Second author and so on"],
        validators=[DataRequired()])

    poster_academic_rank = SelectField("Your academic rank", choices=["Professor", "Associate professor",
        "Assistant professor", "Instructor", "Student", "Employee"], validators=[DataRequired()])

    poster_name = StringField("Your name", validators=[
        DataRequired(), Length(max=64)])

    poster_lastname = StringField("Your lastname", validators=[
        DataRequired(), Length(max=64)])

    poster_email = StringField("Your Email address", validators=[
        DataRequired(), Email(), Length(max=128)])

    poster_affiliation = SelectField("Your affiliation", choices=["Jahrom university", "Other institutions"],
        validators=[DataRequired()])

    abstract = TextAreaField("Abstract", validators=[
        DataRequired(), Length(min=300, max=30000)])

    keywords = StringField("Keywords", validators=[Length(max=64)])

    scientific_field = SelectField("Scientific field", choices=["Natural sciences", "Engineering and technology",
        "Medical and health sciences", "Agricultural sciences", "Formal sciences",
        "Social science", "Humanities"], validators=[DataRequired()])

    journal_file = FileField("Journal file", validators=[FileRequired(), FileAllowed(
        ["pdf"]), FileSize(ARTICLE_FILE_MAXSIZE, message="File size should be 16 Megabytes at maximum.")])

    submit = SubmitField("Submit")

    def validate_publish_date(self, field):
        """Compares the date with the current date. If it was past today, then the date is erroneous."""
        if field.data > date.today():
            raise ValidationError("The date you've entered is in the future!")


class FarsiSubmit(FlaskForm):
    """The submit form for the Farsi version of the website."""

    # Every variable in this class is a field of our form.
    # Each field has a validator keyword argument, which is used to specifies how the field should be examined.
    # There is an message argument for some of the validators, which I had to change since all of the 
    # default ones were in English.
    # There is also a `validate_publish_date` method which checks to see if the inputted date is valid or not. 
    # I had to also subclass the FloatField for reasons I pointed out in the class itself.
    title = StringField("عنوان", validators=[DataRequired(), Length(
        max=64, message="حداکثر تعداد کاراکترهای این فیلد می‌تواند 64 کاراکتر باشد.")])

    publish_date = DateField(
        "تاریخ انتشار", format=r"%Y-%m-%d", validators=[DataRequired()])

    journal_type = RadioField("نوع مقاله", choices=["مجله", "کنفرانس"], validators=[
        DataRequired(message="این فیلد باید پر شود.")])

    scientific_degree = SelectField("نوع مجله/کنفرانس", choices=["ISI", "ISC", "علمی پژوهشی",
         "علمی ترویجی", "هیچکدام"], validators=[DataRequired()])

    impact_factor = FarsiFloatField("ضریب تاثیر")

    abstracting_and_indexing = SelectField("نمایه در بانکهای اطلاعات", choices=["ISI (web of science)", "Scopus",
        "Pubmed"], validators=[DataRequired()])

    doi = StringField("DOI", validators=[DataRequired(), Length(
        max=128, message="حداکثر تعداد کاراکترهای این فیلد می‌تواند 128 کاراکتر باشد.")])

    indexing_certificate_file = FileField("تصویر تایید", validators=[FileRequired(),
        FileAllowed(["jpg", "jpeg", "png"], message="فرمت فایل باید یکی از این فرمت‌ها باشد: jpeg, jpg, png"),
        FileSize(INDEXING_CERTIFICATE_FILE_MAXSIZE, message="حجم فایل باید حداقل 2 مگابایت باشد.")])

    authors_count = IntegerField("تعداد نویسندگان", widget=NumberInput(), validators=[
        DataRequired(), NumberRange(min=1, max=10, message="عدد ورودی باید بین 1 و 10 باشد.")])

    poster_authorship = SelectField("نقش شما", choices=["نویسنده مسئول", "نویسنده اول", "نویسنده دوم به بعد"],
        validators=[DataRequired()])

    poster_academic_rank = SelectField("رتبه علمی شما", choices=["استاد", "دانشیار",
        "استادیار", "مربی", "دانشجو", "کارمند"], validators=[DataRequired()])

    poster_name = StringField("نام شما", validators=[DataRequired(), Length(
        max=64, message="حداکثر تعداد کاراکترهای این فیلد می‌تواند 64 کاراکتر باشد.")])

    poster_lastname = StringField("نام خانوادگی شما", validators=[DataRequired(), Length(
        max=64, message="حداکثر تعداد کاراکترهای این فیلد می‌تواند 64 کاراکتر باشد.")])

    poster_email = StringField("ایمیل شما", validators=[DataRequired(), Email(message="لطفا یک ایمیل معتبر وارد کنید."), Length(
        max=128, message="حداکثر تعداد کاراکترهای این فیلد می‌تواند 128 کاراکتر باشد.")])

    poster_affiliation = SelectField("محل اشتغال شما", choices=["دانشگاه جهرم", "سایر موسسات"],
        validators=[DataRequired()])

    abstract = TextAreaField("چکیده مقاله", validators=[DataRequired(), Length(
        min=300, max=30000, message="تعداد کاراکتر‌های این فیلد می‌تواند بین 300 تا 30000 کاراکتر باشد.")])

    keywords = StringField("کلمات کلیدی", validators=[Length(
        max=64, message="حداکثر تعداد کاراکترهای این فیلد می‌تواند 64 کاراکتر باشد.")])

    scientific_field = SelectField("حوزه علمی", choices=["علوم طبیعی", "مهندسی و تکنولوژی",
        "پزشکی و علوم بهداشت", "علوم کشاورزی", "علوم صوری", "علوم اجتماعی", "علوم انسانی"], validators=[DataRequired()])

    journal_file = FileField("فایل مقاله", validators=[FileRequired(), FileAllowed(
        ["pdf"], message="فرمت فایل باید یکی از این فرمت‌ها باشد: pdf"),
        FileSize(ARTICLE_FILE_MAXSIZE, message="حجم فایل باید حداکثر 16 مگابایت باشد.")])

    submit = SubmitField("ثبت")

    def validate_publish_date(self, field):
        """Compares the date with the current date. If it was past today, then the date is erroneous."""
        if field.data > date.today():
            raise ValidationError("تاریخی که وارد کردید مربوط به آینده است!")


class AdminSubmit(FlaskForm):
    """The submit form for the Admin version of the website."""
    # This is almost the same as the English form except for the `SelectField`s,
    # where I changed all of the `SelectField`s to `StringFiled` to give the admins more liberty.
    # And there is a validate_language method as well which checks for the language to
    # be valid (it should either be English or Farsi).

    title = StringField("Title", validators=[DataRequired(), Length(max=64)])

    publish_date = DateField("Publish date", format=r"%Y-%m-%d", validators=[DataRequired()])

    journal_type = StringField("Journal type", validators=[DataRequired(), Length(max=64)])

    language = StringField("Language", validators=[DataRequired(), Length(max=64)])

    scientific_degree = StringField(
        "Scientific degree", validators=[DataRequired(), Length(max=64)])

    impact_factor = FloatField("Impact factor")

    abstracting_and_indexing = StringField(
        "Abstracting and indexing", validators=[DataRequired(), Length(max=64)])

    doi = StringField("DOI", validators=[DataRequired(), Length(max=128)])

    indexing_certificate_file = FileField("Indexing certificate file", validators=[
        FileAllowed(["jpg", "jpeg", "png"]), FileSize(INDEXING_CERTIFICATE_FILE_MAXSIZE)])

    authors_count = IntegerField("Number of authors", widget=NumberInput(
    ), validators=[DataRequired(), NumberRange(min=1, max=10)])

    poster_authorship = StringField(
        "Poster's authorship", validators=[DataRequired(), Length(max=64)])

    poster_academic_rank = StringField(
        "Poster's academic rank", validators=[DataRequired(), Length(max=64)])

    poster_name = StringField("Poster's name", validators=[DataRequired(), Length(max=64)])

    poster_lastname = StringField(
        "Poster's lastname", validators=[DataRequired(), Length(max=64)])

    poster_email = StringField("Poster's Email address", validators=[
                               DataRequired(), Email(), Length(max=128)])

    poster_affiliation = StringField(
        "Poster's affiliation", validators=[DataRequired(), Length(max=64)])

    abstract = TextAreaField("Abstract", validators=[
                             DataRequired(), Length(min=300, max=30000)])

    keywords = StringField("Keywords", validators=[Length(max=64)])

    scientific_field = StringField(
        "Scientific field", validators=[DataRequired(), Length(max=64)])

    journal_file = FileField("Journal file", validators=[
        FileAllowed(["pdf"]), FileSize(ARTICLE_FILE_MAXSIZE)])

    submit = SubmitField("Submit")

    def validate_publish_date(self, field):
        """Compares the date with the current date. If it was past today, then the date is erroneous."""
        if field.data > date.today():
            raise ValidationError("The date you've entered is in the future!")

    def validate_language(self, field):
        """Validate the languge filed. It should be either English or Farsi"""
        if field.data.lower() != "english" and field.data.lower() != "farsi":
            raise ValidationError(
                "This field should be either English or Farsi.")
