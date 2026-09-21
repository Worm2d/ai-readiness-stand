from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_sitesettings_personal_data_consent"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sitesettings",
            name="require_personal_data_consent",
        ),
        migrations.RemoveField(
            model_name="sitesettings",
            name="personal_data_policy_url",
        ),
        migrations.RemoveField(
            model_name="sitesettings",
            name="personal_data_policy_link_text",
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="privacy_policy_file",
            field=models.FileField(
                blank=True,
                help_text=(
                    "PDF или другой документ с политикой обработки персональных данных. Ссылка на "
                    "скачивание этого файла показывается в форме сбора контактов рядом с текстом "
                    "согласия."
                ),
                null=True,
                upload_to="policy/",
                verbose_name="Файл политики конфиденциальности",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="personal_data_consent_text",
            field=models.TextField(
                default="Я даю согласие на обработку моих персональных данных для подготовки и отправки отчёта.",
                help_text="Показывается во всеплывающем окне при переходе по ссылке «согласие на обработку персональных данных».",
                verbose_name="Текст согласия на обработку персональных данных",
            ),
        ),
    ]
