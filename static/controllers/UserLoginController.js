angular.module('myApp')
  .controller('UserLoginController', ['$scope', '$location', '$rootScope', '$http', '$route', '$cookies',
  function($scope, $location, $rootScope, $http, $route, $cookies) {
        $scope.username = $rootScope.username || null;
        $scope.password = null;
        $scope.error = false;
        $scope.ready = false;

        $scope.login = function(){
            $scope.error = false;

            data = {
                username: $scope.username,
                password: $scope.password
            }

            $http.post('/api/v1/token', data)
                .then(
                function (response, status){
                    $rootScope.token = response.data.token;
                    $rootScope.username = $scope.username;

                    $cookies.put('token', $rootScope.token);

                    $location.path('/chat');
                },
                function(data, status) {
                    $scope.error = true;
                });
        }

        var token = $cookies.get('token');

        if(token){
            data = {
                token
            };

            $http.post('/api/v1/token/verify', data)
            .then(
                function (response, status){
                    $location.path('/chat');
                },
                function(data, status) {
                    $cookies.remove('token');
                    $scope.ready = true;
                });
        }
        else{
            $scope.ready = true;
        }
  }]);