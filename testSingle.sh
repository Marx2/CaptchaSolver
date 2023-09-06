#!/bin/bash
curl -X POST -H "Content-Type: multipart/form-data" -F "image=@test/ZRFJ.png" http://localhost:8000/api/recognize