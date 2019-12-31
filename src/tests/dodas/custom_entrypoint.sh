#!/bin/sh

passString="Filter efficiency (taking into account weights)= (50) / (50) = 1.000e+00 +- 0.000e+00"

source /CMSSW/cmsset_default.sh

cmsenv

cmsRun -j jobReport.xml RSGravitonToZZ_kMpl01_M_1000_TuneCUETP8M1_13TeV_pythia8_GEN-SIM_cfg.py &> cmsRunLogs

if grep -q "$passString" cmsRunLogs; then
  echo "{\"result\":\"success\"}" > /tmp/dodas_test.json
else
  echo "{\"result\":\"fail\"}" > /tmp/dodas_test.json
fi
