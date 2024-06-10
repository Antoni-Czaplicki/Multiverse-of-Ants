Troubleshooting
===============

- If you encounter the following error:
  ::

      PermissionError: [Errno 13] Permission denied

  This error typically occurs when the program tries to bind a network socket to a port that requires higher privileges or is already in use. Here are some steps to resolve this issue:

  1. **Check if the port is already in use:** Use the command `netstat -tuln` to check if the port is already in use. If it is, you will need to stop the process using that port or use a different port for your application.

  2. **Check your permissions:** Ports below 1024 are considered "privileged" ports and you need to be a root user to bind a service to these ports. If you're trying to bind to a port below 1024, try using a port number higher than 1024 or run the program as a superuser.

  3. **Run as a superuser:** If you need to use a privileged port, you can run the program as a superuser with the `sudo` command. However, be aware that this can have security implications.

  4. **Check your firewall settings:** Your firewall may be blocking the port. Check your firewall settings to ensure the port is open.

  5. **Change the HTTP_PORT variable:** If the above steps do not resolve the issue, you can try changing the `HTTP_PORT` variable in the `main.py` file. For example, you can change it to `8000`:
     ::

         HTTP_PORT = 8000

