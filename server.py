from flask import Flask, flash, render_template, request, redirect, session
from mysqlconnection import MySQLConnector
import bcrypt
import re
app = Flask(__name__)