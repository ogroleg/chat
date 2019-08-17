angular.module('myApp')
  .controller('UserRegisterController', ['$scope', '$location', '$rootScope', '$http', '$route',
  function($scope, $location, $rootScope, $http, $route) {
        $scope.username = null;
        $scope.password = null;
        $scope.error = false;

        $scope.register = function(){
            $scope.error = false;

            data = {
                username: $scope.username,
                password: $scope.password
            }

            $http.post('/api/v1/user', data)
                .then(
                function (response, status){
                    $rootScope.username = $scope.username;

                    $location.path('/user/login');
                },
                function(data, status) {
                    $scope.error = true;
                });
        }
  }]);