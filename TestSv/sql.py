# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Baseconfigtable(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BaseConfigTable'


class ConfigimpactTour(models.Model):
    id = models.BigAutoField(db_column='Id')  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.
    tourproperty = models.CharField(db_column='TourProperty', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    tourimpact = models.BooleanField(db_column='TourImpact', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ConfigImpact_Tour'


class ConfigweightService(models.Model):
    id = models.BigAutoField(db_column='Id')  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.
    serviceproperty = models.CharField(db_column='ServiceProperty', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    serviceweight = models.IntegerField(db_column='ServiceWeight', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ConfigWeight_Service'


class ConfigweightTour(models.Model):
    id = models.BigAutoField(db_column='Id')  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.
    tourproperty = models.CharField(db_column='TourProperty', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    weight = models.IntegerField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ConfigWeight_Tour'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
