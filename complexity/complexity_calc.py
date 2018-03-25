import logging
import timeit
import numpy
import math
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('program_log.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

MAX_TIME = 30.0


class TimeoutExc(Exception):
    def __init__(self, message):
        self.message = message


class NotEnoughMeasurementsExc(Exception):
    def __init__(self, message):
        self.message = message


class Measurements:
    def __init__(self, generator, fun, cleaner):
        self.generator = generator
        self.fun = fun
        self.cleaner = cleaner
        self.x = []
        self.y = []

    def measure(self):
        logger.debug('Measurements started')
        total_time = 0.0
        try:
            for i in range(1, 1000):
                self.x.append(i)
                data = self.generator(i)
                timer = timeit.Timer(lambda: self.fun(data))
                measured_time = timer.timeit(number=10)
                total_time += measured_time
                self.y.append(measured_time)
                logger.debug("Measurement for %d elements done" % i)
                self.cleaner()
                if total_time >= MAX_TIME:
                    raise TimeoutExc('Timeout, measurements are not complete')
        except TimeoutExc as te:
            logger.exception(te.message)
            print(te.message)
        logger.debug('Measurements done')


class ComplexityCalc:
    complexities_str = ['O(n)', 'O(n^2)', 'O(n^3)', 'O(log n)', 'O(n*log(n))', 'O(1)']
    functions_str = ['a*n + b', 'a*n^2 + b', 'a*n^3 + b', 'a*logn + b', 'a*nlogn + b', 'a']
    reversed_functions_str = ['(time - b)/a', '((time - b)/a)^(1/2)', '((time - b)/a)^(1/3)', '2^((time - b)/a)',
                              'could not reverse the function', '1/a']
    complexities = [lambda x: x, lambda x: x ** 2, lambda x: x ** 3, lambda x: math.log(x, 2),
                    lambda x: x * math.log(x, 2), lambda x: x]
    polynomial = []
    complexity = 0

    def __init__(self, measurements):
        self.x = measurements.x
        self.y = measurements.y

    def __fit_polynomials(self):
        result = []
        result.append(numpy.polyfit(self.x, self.y, 1))
        result.append(numpy.polyfit(numpy.power(self.x, 2), self.y, 1))
        result.append(numpy.polyfit(numpy.power(self.x, 3), self.y, 1))
        result.append(numpy.polyfit(numpy.log2(self.x), self.y, 1))
        result.append(numpy.polyfit(self.x * numpy.log2(self.x), self.y, 1))
        result.append(numpy.polyfit(self.x, self.y, 0))
        logger.debug('Fitting functions done')
        return result

    def __calculate_errors(self, polynomials):
        result = []
        for i in range(len(polynomials)):
            error_sum = 0
            for j in range(len(self.y)):
                error_sum += abs(numpy.polyval(polynomials[i], self.complexities[i](self.x[j])) - self.y[j])
            result.append(error_sum)
        logger.debug('Calculating errors done')
        return result

    def estimate_complexity(self):
        if len(self.x) < 3:
            raise NotEnoughMeasurementsExc('Too few measurements taken')
        polynomials = self.__fit_polynomials()
        errors = self.__calculate_errors(polynomials)
        min_error_sum = min(errors)
        self.polynomial = polynomials[errors.index(min_error_sum)]
        self.complexity = errors.index(min_error_sum)
        logger.debug('Estimating complexity done')
        print("Estimated complexity: %s" % self.complexities_str[errors.index(min_error_sum)])
        print("Function time(number_of_elements): %s, coefficients: %s" %
              (self.functions_str[self.complexity], str(self.polynomial)))
        if self.complexity == 4:
            print("Function number_of_elements(time): %s" % self.reversed_functions_str[self.complexity])
        else:
            print("Function number_of_elements(time): %s, coefficients: %s" %
                  (self.reversed_functions_str[self.complexity], str(self.polynomial)))


def run(init_fun, fun, cleaner_fun):
    logger.info('Start')
    measurements = Measurements(init_fun, fun, cleaner_fun)
    measurements.measure()
    calc = ComplexityCalc(measurements)
    try:
        calc.estimate_complexity()
    except NotEnoughMeasurementsExc as n:
        logger.exception(n.message)
        exit(1)
    plt.plot(measurements.x, measurements.y)
    plt.ylabel('Time')
    plt.xlabel('Number of elements')
    plt.show()
    logger.debug('Plotting done')
    logger.info('End')
