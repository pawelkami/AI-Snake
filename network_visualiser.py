from pygame import gfxdraw

def render_network(window, x_start, neural_net, last_decision, last_state, neuron_size=5, distance_between_neurons=16):
    if last_decision is None or last_state is None:
        return           
    
    # compute distance between layers
    network_layers = neural_net.layers
    network_layers_count = len(network_layers)
    
    window_width = window.get_rect().right - window.get_rect().left
    window_height = window.get_rect().bottom - window.get_rect().top
    screen_division = (window_width - x_start) / (network_layers_count)
    STEP_SIZE = 1
    step = 0
    for i in range(network_layers_count):
        for j in range(network_layers[i].units):
            y = int(window_height / 2 + (j * distance_between_neurons) - (network_layers[i].units - 1)/2 * distance_between_neurons)
            x = int(x_start + step * screen_division)
            
            fill_factor = 0
            if i == 0:
                fill_factor = int(last_state[j] * 255)
            elif i == network_layers_count - 1:
                fill_factor = int(last_decision[j] * 255)
                
            # draw connections
            if i < network_layers_count - 1:
                for k in range(network_layers[i + 1].units):
                    y2 = int((window_height / 2) + (k * distance_between_neurons) - (network_layers[i + 1].units - 1)/2 * distance_between_neurons)
                    x2 = int(x_start + (step + STEP_SIZE) * screen_division)
                    
                    fill_factor_line = 60
                    # input layer
                    if i == 0:
                        fill_factor_line = fill_factor / 2 + 40
                    gfxdraw.line(window, x + 2, y, x2, y2, (fill_factor_line, fill_factor_line, fill_factor_line, fill_factor_line))
            
            gfxdraw.filled_circle(window, x, y, neuron_size, (fill_factor, fill_factor, fill_factor))
            gfxdraw.aacircle(window, x, y, neuron_size, (255, 255, 255))
        step += STEP_SIZE