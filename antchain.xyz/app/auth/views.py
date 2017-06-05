#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/24/17 10:55 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : views.py
# @Software: PyCharm

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user,current_user
from . import auth
from ..models import User
from .forms import RegisterForm, LoginForm,ChangePasswordForm,ChangeEmailForm,PasswordResetForm,PasswordResetRequestForm

@auth.before_app_request
def before_request():
    # flash('这是测试网，请注意！', 'danger')
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('登陆成功！欢迎回来，%s!' % user.username, 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('登陆失败！用户名或密码错误，请重新登陆。', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登陆。', 'success')
    # flash('You have been logged out.')
    return redirect(url_for('main.index'))

from ..email import send_email, send_async_email


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data)
        user.password = form.password.data
        user.save()
        token = user.generate_confirmation_token()
        # send_email(current_user.email, "Confirm your email", "auth/email/confirm",
        #            user=current_user, token=token)
        send_async_email(current_user.email, "Confirm your email", "auth/email/confirm",
            user=current_user, token=token)

        flash("A confirmation email has been sent to your email.",'success')
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have already confirmed your account. Thanks!",'success')
    else:
        flash("The confirmation link is invalid or has expired.",'danger')
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    # send_email(current_user.email, "Confirm your email", "email/confirm",
    #         user=current_user, token=token)
    send_async_email(current_user.email, "Confirm your email", "auth/email/confirm",
        user=current_user, token=token)
    flash("A new confirmation email has already been sent to your email.",'success')
    return redirect(url_for("main.index"))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.save()
            flash('Your password has been updated.','success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_async_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_async_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.','success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.','danger')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.','suceess')
    else:
        flash('Invalid request.','danger')
    return redirect(url_for('main.index'))
