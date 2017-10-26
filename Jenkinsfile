stage('Build Image') {
    customData = [:]
    node ('docker') {
        try {
            checkout scm
            sh 'export AWS_PROFILE="uis-generic"'
            sh 'eval $(aws ecr get-login --registry-ids 957958309439 --region eu-west-2)'
            if ( sh (
                script: "docker build -t 957958309439.dkr.ecr.eu-west-2.amazonaws.com/uis/cache-school-data:latest .",
                returnStatus: true) != 0 ) {
                throw new Exception("Docker build failed")
            } else {
                echo 'Docker build successful'
            }
            if ( sh (
                script: "docker push 957958309439.dkr.ecr.eu-west-2.amazonaws.com/uis/cache-school-data:latest",
                returnStatus: true) != 0 ) {
                throw new Exception("Docker push failed")
            } else {
                echo 'Docker push successful'
            }
            customData['image_build_status'] = 'SUCCESS'
            customData['image_build_result_ordinal'] = '0'
        } catch (Exception err) {
             echo 'Catching exceptions'
             currentBuild.result = 'FAILURE'
             customData['image_build_status'] = 'FAILURE'
             customData['image_build_result_ordinal'] = '5'
        } finally {
             step([$class: 'InfluxDbPublisher',
                customData: customData,
                customDataMap: null,
                customPrefix: "cache-school-data",
                target: 'ss-metrics'])
      }
   }
}
