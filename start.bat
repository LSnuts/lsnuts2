@echo off
powershell -ExecutionPolicy Bypass -Command "& {Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File ""%~dp0start.ps1""'}"