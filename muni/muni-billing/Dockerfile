# ***************************************************
# TEMPLATE: legacy/soadev/env/Dockerfile.txt
# ***************************************************

ARG BASE_IMAGE=ubuntu:20.04

# ***************************************************
# Builder stage, common for local dev & circle-ci
# ***************************************************
FROM ${BASE_IMAGE} AS builder

ARG HOST_UID=0
ARG HOST_GID=0
ARG RUBY_VERSION=2.4.9
ARG OPEN_SSL_VERSION=openssl-1.1.1g
ARG BUNDLE_GEMS__CONTRIBSYS__COM
ARG BUNDLE_GEMS__RAILSLTS__COM

# ENV is for future running containers. ARG for this current build.
# both ENV & ARG are available during build
# ARG are not available after the build
# funding requests ignored since they have been observed to crash the build
ENV \
    APP_ROOT=/usr/src/app \
    APP_NAME="billing" \
    USER_NAME="gitdeploy" \
    DEBIAN_FRONTEND=noninteractive \
    BUNDLE_IGNORE_FUNDING_REQUESTS=1

# general packages
RUN \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y curl nano wget software-properties-common build-essential \
            default-libmysqlclient-dev mysql-client libxslt-dev libxml2-dev \
            tzdata unzip lsb-release git pdftk rsync libmagic-dev

# install Python 3.9 to meet google-cloud-cli requirements (needs Python >= 3.9)
# We need to install python3-pip first to avoid conflicts later
RUN \
  apt-get install -y software-properties-common python3-pip && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y python3.9 python3.9-distutils python3.9-dev python3.9-venv && \
  update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
  update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2 && \
  update-alternatives --set python3 /usr/bin/python3.9

# install jq (needed for shell scripts that interact with gcloud)
RUN apt-get install -y jq

# install Google Cloud CLI using official installer (bypasses apt Python dependency issues)
RUN \
  cd /tmp && \
  if [ "$(uname -m)" = "aarch64" ]; then \
    export GCLOUD_FILE="google-cloud-cli-linux-arm.tar.gz"; \
  elif [ "$(uname -m)" = "x86_64" ]; then \
    export GCLOUD_FILE="google-cloud-cli-linux-x86_64.tar.gz"; \
  else \
    export GCLOUD_FILE="unknown-architecture"; \
  fi && \
  wget --progress=bar:force:noscroll "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/$GCLOUD_FILE" && \
  tar -xzf "$GCLOUD_FILE" && \
  ./google-cloud-sdk/install.sh --quiet --path-update=true && \
  echo 'export PATH="$PATH:/google-cloud-sdk/bin"' >> /etc/environment && \
  ln -s /tmp/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud && \
  ln -s /tmp/google-cloud-sdk/bin/gsutil /usr/local/bin/gsutil && \
  rm -f "$GCLOUD_FILE"

# install wkhtmltox from https://wkhtmltopdf.org/downloads.html
# note the hard dependence on 'focal' (aka Ubuntu 20.04). This needs to be kept in sync
# with BASE_IMAGE
RUN if [ "$(uname -m)" = "aarch64" ]; then \
      export DEB_FILE="wkhtmltox_0.12.6-1.focal_arm64.deb"; \
    elif [ "$(uname -m)" = "x86_64" ]; then \
      export DEB_FILE="wkhtmltox_0.12.6-1.focal_amd64.deb"; \
    else \
      export DEB_FILE="unknown-architecture"; \
    fi && \
    cd /tmp && \
    wget --progress=bar:force:noscroll "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/$DEB_FILE" && \
    apt-get install -y "./$DEB_FILE"  && \
    ln -nsf /usr/local/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf_old && \
    echo "Installed $DEB_FILE" >> /build.log

# install OPEN_SSL_VERSION for all users
# compliling from source is the most portable way of installing this on x86 and
# arm architectures
RUN \
    cd /tmp && \
    wget https://www.openssl.org/source/${OPEN_SSL_VERSION}.tar.gz && \
    tar zxvf ${OPEN_SSL_VERSION}.tar.gz && \
    cd ${OPEN_SSL_VERSION} && \
    ./config --prefix=/opt/openssl/${OPEN_SSL_VERSION} --openssldir=/opt/openssl/${OPEN_SSL_VERSION} && \
    make && \
    make install && \
    rm -rf /opt/openssl/${OPEN_SSL_VERSION}/certs && \
    ln -s /etc/ssl/certs /opt/openssl/${OPEN_SSL_VERSION}/certs

# install RVM for all users
RUN \
    curl -sSL https://keybase.io/mpapis/pgp_keys.asc | gpg --import && \
    curl -sSL https://keybase.io/piotrkuczynski/pgp_keys.asc | gpg --import && \
    curl -sSL https://get.rvm.io | bash -s stable

# install ruby for all users
# also ugrade to more recent version fo rubygems & install required versions of
RUN \
    /bin/bash -c "source /etc/profile.d/rvm.sh && \
    rvm install ${RUBY_VERSION} --with-openssl-dir=/opt/openssl/${OPEN_SSL_VERSION} && \
    gem update --system 3.3.26 --no-document"

# install ruby 2.6.10 for all users
RUN \
    /bin/bash -c "source /etc/profile.d/rvm.sh && \
    rvm install 2.6.10 --with-openssl-dir=/opt/openssl/${OPEN_SSL_VERSION} && \
    gem update --system 3.3.26 --no-document"

# install dockerize
RUN if [ "$(uname -m)" = "aarch64" ]; then \
      export TAR_FILE="dockerize-linux-armhf-v0.6.1.tar.gz"; \
    elif [ "$(uname -m)" = "x86_64" ]; then \
      export TAR_FILE="dockerize-linux-amd64-v0.6.1.tar.gz"; \
    else \
      export TAR_FILE="unknown-architecture"; \
    fi && \
    cd /tmp && \
    wget --progress=bar:force:noscroll "https://github.com/jwilder/dockerize/releases/download/v0.6.1/$TAR_FILE" && \
    tar -C /usr/local/bin -xzvf $TAR_FILE && \
    echo "Installed $TAR_FILE" >> /build.log

# create local user/group
RUN if [ ${HOST_GID} -eq 0 ]; then \
      # When HOST_GID is not set we do the default user creation
      echo "Argument HOST_GID not set, using defaults" >> /build.log; \
      useradd --create-home --shell /bin/bash $USER_NAME; \
    else \
      # When HOST_GID is set we create an user with specific group and user id \
      # note that when setting HOST_GID, you also must set HOST_UID
      echo "Argument HOST_GID=${HOST_GID}; HOST_UID=${HOST_UID}" >> /build.log; \
      export CONTAINER_GROUPNAME=$(cat /etc/group | grep ":$HOST_GID:" | cut -d ":" -f 1) && \
      if [ -z "$CONTAINER_GROUPNAME" ]; then \
        # when such group does not exist inside the container - create it \
        # technically, we should be doing the same thing for the HOST_UID, but it has been  \
        # observed that HOST_UID is always above 1000 and never collides with existing \
        # container users \
        echo "gid $HOST_GID not found, creating anew ..." >> /build.log; \
        groupadd --gid ${HOST_GID} $USER_NAME; \
      else \
        echo "gid $HOST_GID already present, it will be reused ..." >> /build.log; \
      fi; \
      useradd --create-home --no-user-group --shell /bin/bash --gid ${HOST_GID} --uid ${HOST_UID} $USER_NAME; \
      echo "created $(id $USER_NAME)" >> /build.log; \
    fi

# add user to the RVM group
RUN usermod -a -G rvm $USER_NAME

# switch to newly created user
USER $USER_NAME

# install fonts
COPY --chown=${USER_NAME} legacy/vendor/assets/fonts/ /home/$USER_NAME/.fonts

# To install the gems, we copy gemfiles locally & run bundler
COPY --chown=${USER_NAME} legacy/Gemfile /tmp/gemfiles/billing/Gemfile
COPY --chown=${USER_NAME} legacy/Gemfile.lock /tmp/gemfiles/billing/Gemfile.lock

# install $RUBY_VERSION gems
RUN \
    /bin/bash -c "source /etc/profile.d/rvm.sh && \
    export BUNDLE_GEMS__CONTRIBSYS__COM=$BUNDLE_GEMS__CONTRIBSYS__COM && \
    export BUNDLE_GEMS__RAILSLTS__COM=$BUNDLE_GEMS__RAILSLTS__COM && \
    echo $RUBY_VERSION > /tmp/gemfiles/billing/.ruby-version && \
    cd /tmp/gemfiles/billing && \
    bundle install"

# install 2.6.10 gems
RUN \
    /bin/bash -c "source /etc/profile.d/rvm.sh && \
    export BUNDLE_GEMS__CONTRIBSYS__COM=$BUNDLE_GEMS__CONTRIBSYS__COM && \
    export BUNDLE_GEMS__RAILSLTS__COM=$BUNDLE_GEMS__RAILSLTS__COM && \
    echo 2.6.10 > /tmp/gemfiles/billing/.ruby-version && \
    cd /tmp/gemfiles/billing && \
    bundle install"

# Add RVM to PATH (for future sessions). Make sure this is the last PATH variable change.
# Also load RVM into a shell session *as a function* (for future sessions). Add this to both
# active and non-interractve shell configurations
RUN \
    export TMP_CONFIG=/home/$USER_NAME/tmp_config && \
    echo > $TMP_CONFIG && \
    echo "#Add RVM to PATH & load RVM into a shell session *as a function*" >> $TMP_CONFIG && \
    echo "export PATH=\"\$PATH:/usr/local/rvm/bin\"" >> $TMP_CONFIG && \
    echo "[[ -s \"/etc/profile.d/rvm.sh\" ]] && source \"/etc/profile.d/rvm.sh\"" >> $TMP_CONFIG && \
    echo >> $TMP_CONFIG && \
    cat $TMP_CONFIG >> /home/$USER_NAME/.bashrc && \
    cat $TMP_CONFIG >> /home/$USER_NAME/.profile && \
    rm $TMP_CONFIG


# ***************************************************
# Development stage adds specifics for local development
# ***************************************************
FROM builder AS development

# Configure ruby console
RUN echo "IRB.conf[:USE_AUTOCOMPLETE] = false" > /home/$USER_NAME/.irbrc && \
    echo "IRB.conf[:USE_COLORIZE] = false" >> /home/$USER_NAME/.irbrc

WORKDIR $APP_ROOT


# Default action if nothing else specified on command line
CMD ["irb"]

# ***************************************************
# circle-ci stage adds specifics for circle-ci build
# environemnt
# ***************************************************
FROM builder AS circle-ci

# we need all the source baked into the image
COPY --chown=${USER_NAME} legacy $APP_ROOT

WORKDIR $APP_ROOT


# created at 2025-09-18_17:37:36 by legacy_setup
