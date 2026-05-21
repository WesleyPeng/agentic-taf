#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Wesley Peng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#------------------------------------------------------
# Automation Builder (for Docker Compose)
#------------------------------------------------------
CYAN='\e[1;36m'
NC='\e[0m'
ARTIFACTS=artifacts

TAG_BUILD=$1
echo -e "${CYAN}Set Build Number(${TAG_BUILD})${NC}"
echo "" >> src/main/python/setup.cfg
echo "[egg_info]" >> src/main/python/setup.cfg
echo "tag_build=${TAG_BUILD}" >> src/main/python/setup.cfg

echo -e "${CYAN}Install Dependencies${NC}"
python -m pip install enum34
python -m pip install paramiko
python -m pip install PyYAML
python -m pip install requests
#python -m pip install selenium
python -m pip install Appium-Python-Client

echo -e "${CYAN}Build uiXautomation(PyXTaf*.whl file) project & Run unit tests${NC}"
python -m pip install pybuilder
pyb -v clean publish

# ARGS=${@:2}
# echo -e "${CYAN}Run tests according to arguments(${ARGS})${NC}"
# python -m pip install dist/dist/PyXTaf*.whl
# python -m PyXTaf ${ARGS}

echo -e "${CYAN}Run BDD/ATDD tests and save artifacts/results${NC}"
python -m pip install dist/dist/PyXTaf*.whl
mkdir -p ${ARTIFACTS}
mv build/reports/*.xml ${ARTIFACTS}/

pushd . >/dev/null
cd ./src/test/python

echo -e "${CYAN}Run BDD test(s)${NC}"
python -m pip install allure-behave
python -m bpt.bdd -f allure_behave.formatter:AllureFormatter  \
-o ../../../${ARTIFACTS}/allure -t ~@wip  \
-D browser="chrome" -D is_remote="True"

echo -e "${CYAN}Run ATDD test(s)${NC}"
python -m pip install robotframework
python -m robot -d ../../../${ARTIFACTS}/robot  \
-v is_remote:True -v enable_screenshot:True bpt/atdd/robot/bing.robot
popd > /dev/null

mv dist/dist/PyXTaf*.whl ${ARTIFACTS}/
chmod a+w -R ${ARTIFACTS}/
