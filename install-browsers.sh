#!/usr/bin/bash

declare -A chrome_versions

# Enter the list of browsers to be downloaded
### Using Chromium as documented here - https://www.chromium.org/getting-involved/download-chromium
chrome_versions=( ['114.0.5735.90']='1135580' ['113.0.5672.63']='1121461' )
chrome_drivers=( "114.0.5735.90" "113.0.5672.63" )
firefox_versions=( "117.0" "118.0" )
gecko_drivers=( "0.32.2" )

# Download Chrome
for br in "${!chrome_versions[@]}"
do
    echo "Downloading Chrome version $br"
    echo "Chrome URL => https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F${chrome_versions[$br]}%2Fchrome-linux.zip?alt=media"
    mkdir -p "/opt/chrome/$br"
    curl -Lo "/opt/chrome/$br/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F${chrome_versions[$br]}%2Fchrome-linux.zip?alt=media"
    unzip -q "/opt/chrome/$br/chrome-linux.zip" -d "/opt/chrome/$br/"
    mv /opt/chrome/$br/chrome-linux/* /opt/chrome/$br/
    rm -rf /opt/chrome/$br/chrome-linux "/opt/chrome/$br/chrome-linux.zip"
    ls -al "/opt/chrome/$br/*"
done

# Download Chromedriver
for dr in ${chrome_drivers[@]}
do
    echo "Downloading Chromedriver version $dr"
    echo "Chromedriver URL => https://chromedriver.storage.googleapis.com/$dr/chromedriver_linux64.zip"
    mkdir -p "/opt/chromedriver/$dr"
    curl -Lo "/opt/chromedriver/$dr/chromedriver_linux64.zip" "https://chromedriver.storage.googleapis.com/$dr/chromedriver_linux64.zip"
    unzip -q "/opt/chromedriver/$dr/chromedriver_linux64.zip" -d "/opt/chromedriver/$dr/"
    chmod +x "/opt/chromedriver/$dr/chromedriver"
    rm -rf "/opt/chromedriver/$dr/chromedriver_linux64.zip"
    ls -al "/opt/chromedriver/$dr/chromedriver"
    "/opt/chromedriver/$dr/chromedriver" --version
done

# Download Firefox
for br in ${firefox_versions[@]}
do
    echo "Downloading Firefox version $br"
    echo "Firefox URL => http://ftp.mozilla.org/pub/firefox/releases/$br/linux-x86_64/en-US/firefox-$br.tar.bz2"
    mkdir -p "/opt/firefox/$br"
    curl -Lo "/opt/firefox/$br/firefox-$br.tar.bz2" "http://ftp.mozilla.org/pub/firefox/releases/$br/linux-x86_64/en-US/firefox-$br.tar.bz2"
    tar -jxf "/opt/firefox/$br/firefox-$br.tar.bz2" -C "/opt/firefox/$br/"
    mv "/opt/firefox/$br/firefox" "/opt/firefox/$br/firefox-temp"
    mv /opt/firefox/$br/firefox-temp/* /opt/firefox/$br/
    rm -rf "/opt/firefox/$br/firefox-$br.tar.bz2"
    ls -al "/opt/firefox/$br/*"
done

# Download Geckodriver
for dr in ${gecko_drivers[@]}
do
    echo "Downloading Geckodriver version $dr"
    echo "Gecko Driver URL -> https://github.com/mozilla/geckodriver/releases/download/v$dr/geckodriver-v$dr-linux64.tar.gz"
    mkdir -p "/opt/geckodriver/$dr"
    curl -Lo "/opt/geckodriver/$dr/geckodriver-v$dr-linux64.tar.gz" "https://github.com/mozilla/geckodriver/releases/download/v$dr/geckodriver-v$dr-linux64.tar.gz"
    tar -zxf "/opt/geckodriver/$dr/geckodriver-v$dr-linux64.tar.gz" -C "/opt/geckodriver/$dr/"
    chmod +x "/opt/geckodriver/$dr/geckodriver"
    rm -rf "/opt/geckodriver/$dr/geckodriver-v$dr-linux64.tar.gz"
    ls -al "/opt/geckodriver/$dr/geckodriver"
    "/opt/geckodriver/$dr/geckodriver" --version
done

