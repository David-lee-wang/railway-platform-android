package com.railway.platform;

import com.chaquo.python.PyApplication;

/**
 * Custom Application class that initializes Chaquopy Python automatically.
 * Extends PyApplication so that Python.start(new AndroidPlatform(context))
 * is called before any Activity or Python code runs.
 */
public class RailwayApplication extends PyApplication {
}
